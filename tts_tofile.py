###Created by xiewoc(github.com/xiewoc),use under permission
###Still there's a lot of codes borrowed from cosyvoice and Step-Audio

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),'Step-Audio'))
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'Step-Audio'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tokenizer import StepAudioTokenizer
from pydub import AudioSegment
from datetime import datetime
from tts import StepAudioTTS
import torchaudio
import logging
import re

logging.getLogger("pydub").setLevel(logging.WARNING) 

tmp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'temp')
model_path = os.path.dirname(os.path.abspath(__file__))

global if_init
if_init = False

def init():
    global if_init
    if if_init:
        pass
    else:
        global tts_engine
        encoder = StepAudioTokenizer(os.path.join(model_path, "models", "Step-Audio-Tokenizer"))
        tts_engine = StepAudioTTS(os.path.join(model_path, "models", "Step-Audio-TTS-3B"), encoder)
        if_init = True

def wav2mp3(wav_path, script_path):
    try:
        audio = AudioSegment.from_wav(wav_path)
        mp3_path = os.path.join(script_path, "output.mp3")
        audio.export(mp3_path, format="mp3", parameters=["-loglevel", "quiet"])
        if os.path.exists(wav_path):
            os.remove(wav_path)
        return mp3_path
    except Exception as e:
        logging.error(f"Error converting WAV to MP3: {e}")
        raise
# 保存音频
def save_audio(audio_type, audio_data, sr):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    save_path = os.path.join(tmp_dir, audio_type, f"{current_time}.wav")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torchaudio.save(save_path, audio_data, sr)
    return save_path

# 普通语音合成
def tts_common(text, speaker, emotion, language, speed):
    text = (
        (f"({emotion})" if emotion else "")
        + (f"({language})" if language else "")
        + (f"({speed})" if speed else "")
        + text
    )
    init()
    global tts_engine
    output_audio, sr = tts_engine(text, speaker)
    audio_type = "common"
    common_path = save_audio(audio_type, output_audio, sr)
    return common_path

# RAP / 哼唱模式
def tts_music(text_input_rap, speaker, mode_input):
    text_input_rap = f"({mode_input})" + text_input_rap
    init()
    global tts_engine
    output_audio, sr = tts_engine(text_input_rap, speaker)
    audio_type = "music"
    music_path = save_audio(audio_type, output_audio, sr)
    return music_path

# 语音克隆
def tts_clone(text, wav_file, speaker_prompt, emotion, language, speed):
    clone_speaker = {
        "wav_path": wav_file,
        "speaker": "custom_voice",
        "prompt_text": speaker_prompt,
    }
    clone_text = (
        (f"({emotion})" if emotion else "")
        + (f"({language})" if language else "")
        + (f"({speed})" if speed else "")
        + text
    )
    init()
    global tts_engine
    output_audio, sr = tts_engine(clone_text, "", clone_speaker)
    audio_type = "clone"
    clone_path = save_audio(audio_type, output_audio, sr)
    return clone_path

if __name__ == '__main__':
    print("This is a model ,you can't run this seperately.")