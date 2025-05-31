import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import re
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import FileResponse
import uvicorn
import tts_tofile as ts

app = FastAPI()

global if_remove_think_tag ,if_preload
if_preload = False
if_remove_think_tag = False

global on_init
on_init = True

def remove_thinktag(text):
    if text:
        cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        return cleaned_text
    else:
        return ''

class SpeechRequest(BaseModel):
    model: str
    input: str
    voice: str

class ConfigRequest(BaseModel):
    speaker:str
    dialect:str
    mood:str
    speed:str
    if_remove_think_tag:bool
    if_preload:bool

def run_service():
    uvicorn.run(app, host="0.0.0.0", port=5055)
    
@app.post("/audio/speech")
async def generate_speech(request: Request, speech_request: SpeechRequest):
    
    script_path = os.path.dirname(os.path.abspath(__file__))
    #wav_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"sounds")

    global speaker,dialect,mood,speed,if_remove_think_tag

    try:
        global if_remove_think_tag
        if if_remove_think_tag == True:
            input_text = remove_thinktag(speech_request.input)
        else:
            input_text = speech_request.input

        if input_text != '':
            sound_path = ts.wav2mp3(
                ts.tts_common(input_text, speaker, mood, dialect, speed),#using speakers mode
                script_path
                )
        if input_text == '':
            raise HTTPException(status_code=500, detail="Input text is empty")
        
        if not sound_path or not os.path.exists(sound_path) or not os.access(sound_path, os.R_OK):
            raise HTTPException(status_code=500, detail="Failed to generate speech")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    # 使用FileResponse返回生成的语音文件
    return FileResponse(path=sound_path, media_type='audio/mp3', filename="output.mp3")

@app.post("/config")
async def set_config(request: Request, config_request: ConfigRequest):
    """
        class ConfigRequest(BaseModel):
        speaker:str
        dialect:str
        mood:str
        speed:str
        if_remove_think_tag:bool
        if_preload:bool
    """
    global speaker,dialect,mood,speed,if_remove_think_tag,if_preload

    if config_request.speaker:
        speaker = config_request.speaker
    if config_request.dialect:
        dialect = config_request.dialect
    if config_request.mood:
        mood = config_request.mood
    if config_request.speed:
        speed = config_request.speed
    if config_request.if_remove_think_tag:
        if_remove_think_tag = config_request.if_remove_think_tag
    if config_request.if_preload:
        if_preload = config_request.if_preload
    
    print(
        "Config updated:\n",
        f"Speaker:{speaker}\n",
        f"Dialect:{dialect}\n",
        f"Mood:{mood}\n",
        f"Speed:{speed}\n",
        f"If_remove_think_tag:{if_remove_think_tag}\n",
        f"If_preload:{if_preload}"
        )
    
    if if_preload:
        global on_init
        if on_init:
            ts.init()
            on_init = False
        else:
            pass

if __name__ == "__main__":
    print("This is a model ,you can't run this seperately.")