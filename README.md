# astrbot_plugin_tts_Step_Audio

## Astrbot的tts功能补充（使用Step-Audio-3B本地模型）

# 配置

### 需要ffmpeg 和 git在系统路径下！

(可选)先将[Step-Audio环境配置](https://github.com/xiewoc/Step-Audio?tab=readme-ov-file#-42-dependencies-and-installation)中的操作做一遍，检查是否有遗漏的库未安装

再使用命令 `pip  install -r requirements.txt` 在shell安装所需库（包含前一步的，但可能不全）

与官方tts方法一致，配置时用openai_tts_api，api填入127.0.0.1:5050，超时建议在240s左右，key随意

# 使用

## eg. 

`/tts`以开启/关闭文字转语音

# 注意

这个插件比较吃电脑性能与显存（如有），远高于官方所说1.5GB + 8GB

如图：

<img width="593" alt="image" src="https://github.com/user-attachments/assets/1826eccf-7bae-47ca-8a07-40f817a6519b" />

# 更新内容

## for 1.0.0

基础功能（tts，还在研究func_call），schema

# 球球了，给孩子点个star吧！

# 自带音频

目前作者只给了`绯莎_prompt.wav`，后续会持续更新，也可以自己创建，构建如下：

语音格式应为`xxx_prompt.wav`文件，码率为16KHz，且为单声道，在speakers_info.json文件内容仿照前面添加如下：

```
    "xxx": "[语音内容]",
```

eg.

```
{
    "绯莎":"如果有奖励的话，鲷鱼烧就可以了"
}
```

# 当然，A lot of codes borrowed from Cosyvoice and Step-Fun-Audio
