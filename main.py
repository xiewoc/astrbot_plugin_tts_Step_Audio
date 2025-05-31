#有关tts的详细配置请移步service.py
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api.provider import ProviderRequest
from astrbot.api.provider import LLMResponse
from astrbot.api.message_components import *
from multiprocessing import Process
from astrbot.api.all import *
from typing import Optional
import subprocess
import requests
import asyncio
import atexit
import glob
import json
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

global on_init ,reduce_parenthesis
on_init = True
reduce_parenthesis = False

async def request_tts(text: str):
    payload = {
        "model": "",
        "input": text,
        "voice": ""
    }
    global server_ip
    if server_ip != '':
        url = 'http://' + server_ip + ':5055/audio/speech'
        try:
            # 设置超时时间为60秒
            response = requests.post(url, json=payload, stream=True, timeout=(10, 60))
            if response.status_code == 200:
                # 打开一个本地文件用于写入
                file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'file_receive.mp3')
                with open(file_path, 'wb') as file:
                    # 逐块写入文件
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                    return file_path
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return ''
        except requests.exceptions.Timeout:
            print("请求超时，服务器未在60秒内响应")
            return ''
        except requests.exceptions.RequestException as e:
            print(f"请求发生错误: {e}")
            return ''
    else:
        print("Server url is void, please check your settings")
        return ''

async def request_config(speaker: str,dialect: str,mood: str,speed: str,if_remove_think_tag: bool,if_preload: bool,ip:str):
    payload = {
            "speaker":speaker,
            "dialect":dialect,
            "mood":mood,
            "speed":speed,
            "if_remove_think_tag":if_remove_think_tag,
            "if_preload":if_preload
            }
    url = 'http://' + ip + ':5055/config'
    await asyncio.sleep(15)#等待fastapi启动
    ret = requests.post(url, json=payload, timeout=(10, 30))
    return ret

def download_model_and_repo():
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)),'Step-Audio')):#克隆仓库
        pass
    else:
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'Step-Audio')
        run_command(f"git clone --recursive https://github.com/xiewoc/Step-Audio.git {base_dir}")#改为我的魔改版了（open->utf-8;read_dir->../speakers/）
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)),'models','Step-Audio-TTS-3B')) or os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)),'models','Step-Audio-Tokenizer')):
        pass
    else:
        from modelscope import snapshot_download
        snapshot_download('stepfun-ai/Step-Audio-TTS-3B', local_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),'models','Step-Audio-TTS-3B'))#下载模型
        snapshot_download('stepfun-ai/Step-Audio-Tokenizer', local_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)),'models','Step-Audio-Tokenizer'))#下载模型

def run_command(command):#cmd line  git required!!!!
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    if error:
        print(f"Error: {error.decode()}")
    return output.decode()

# 锁文件路径
lock_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"child_process.lock")

def cleanup():
    """清理函数，用于在程序结束时删除锁文件"""
    if os.path.exists(lock_file_path):
        os.remove(lock_file_path)

def child_process_function():
    import service 
    service.run_service()

def start_child_process():
    global on_init 

    """启动子进程的函数"""
    if os.path.exists(lock_file_path):
        if on_init == True:
            cleanup()
            on_init = False
            pass
        else:
            print("Another instance of the child process is already running.")
            return None
    
    # 创建锁文件
    with open(lock_file_path, 'w') as f:
        f.write("Locked")
    
    # 注册清理函数
    atexit.register(cleanup)
    
    # 创建并启动子进程
    p = Process(
        target=child_process_function,
        args=()
        )
    p.start()
    print("Sub process (service.py) started")
    return p

def terminate_child_process_on_exit(child_process):
    """注册一个函数，在主进程退出时终止子进程"""
    def cleanup_on_exit():
        if child_process and child_process.is_alive():
            child_process.terminate()
            child_process.join()  # 确保子进程已经完全终止
            print("Service.py process terminated.")
        cleanup()
    atexit.register(cleanup_on_exit)

@register("astrbot_plugin_tts_Step_Audio", "xiewoc ", "使用Step-Audio对Astrbot的tts进行补充", "1.0.0", "https://github.com/xiewoc/astrbot_plugin_tts_Step_Audio")
class astrbot_plugin_tts_Step_Audio(Star):
    def __init__(self, context: Context, config: dict):
        super().__init__(context)

        download_model_and_repo()

        self.config = config
        sub_config_serve = self.config.get('server_cfg', {})
        generate_config = self.config.get('gen_cfg',{})
        #读取设置

        global if_preload ,if_remove_think_tag
        if_remove_think_tag = self.config['if_remove_think_tag']
        if_preload = self.config['if_preload']

        global server_ip ,if_seperate_serve
        server_ip = sub_config_serve.get('server_ip', '')
        if_seperate_serve = sub_config_serve.get('if_seperate_serve', '')

        global speaker ,mood ,language ,speed
        speaker = generate_config.get('speaker','')
        mood = generate_config.get('mood','')
        language = generate_config.get('language','')
        speed = generate_config.get('speed','')

        #print(f"if_preload: {if_preload}, if_remove_think_tag: {if_remove_think_tag}, server_ip: {server_ip}, if_seperate_serve: {if_seperate_serve}")
        #print(f"speaker: {speaker}, mood: {mood}, language: {language}, speed: {speed}")

        #加载完成时
        @filter.on_astrbot_loaded()
        async def on_astrbot_loaded(self):
            global if_preload ,if_remove_think_tag ,server_ip ,if_seperate_serve ,speaker ,mood ,language ,speed
            if if_seperate_serve == True:
                pass
            else:
                child_process = start_child_process()
                if child_process:
                    terminate_child_process_on_exit(child_process)

            await request_config(speaker ,language ,mood ,speed ,if_remove_think_tag ,if_preload ,server_ip)
            

    """
    @llm_tool(name="send_voice_msg") 
    async def send_voice_msg(self, event: AstrMessageEvent, text: str, dialect: Optional[str] = None ) -> MessageEventResult:#这边optional了因为怕有的llm会看不懂
        '''发送语音消息。

        Args:
            text(string): 要转语音的文字
            dialect(string,optional): 方言（若未说明则填入 '普通话'）
        '''
        if text != '':
            if dialect != None:
                global server_ip
                request_config(dialect ,'' , '', 'instruct2', server_ip)
            path = await request_tts(text)#返回的是mp3文件
            chain = [
                Record.fromFileSystem(path)
                ]
            yield event.chain_result(chain)
    """