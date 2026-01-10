import os
import sys

# [1단계] FFmpeg 경로를 파이썬 시스템 환경변수에 최우선으로 등록합니다.
# 현재 폴더(C:\python\reachy-mini-Study)에 ffmpeg.exe가 있다고 가정합니다.
current_dir = r"C:\python\reachy-mini-Study"
os.environ["PATH"] += os.pathsep + current_dir

import pydub
# pydub에게 직접 실행 파일 위치를 알려줍니다.
pydub.AudioSegment.converter = os.path.join(current_dir, "ffmpeg.exe")
pydub.AudioSegment.ffprobe = os.path.join(current_dir, "ffprobe.exe")

import cv2
import numpy as np
import time
import speech_recognition as sr
from gtts import gTTS
import io
from reachy_mini import ReachyMini

def speak(text, mini):
    print(f"[로봇 답변]: {text}")
    try:
        tts = gTTS(text=text, lang='ko')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # 여기서 ffmpeg를 사용하여 변환합니다.
        audio = pydub.AudioSegment.from_file(fp, format="mp3")
        audio_array = np.array(audio.get_array_of_samples())

        chunk_size = 1024
        for i in range(0, len(audio_array), chunk_size):
            chunk = audio_array[i:i+chunk_size]
            mini.media.push_audio_sample(chunk)
    except Exception as e:
        print(f"[오디오 출력 에러]: {e}")

def listen_command(mini):
    recognizer = sr.Recognizer()
    print("\n[듣는 중...] 명령을 말씀하세요 (3초)")
    
    audio_buffer = []
    start_time = time.time()
    while time.time() - start_time < 3:
        sample = mini.media.get_audio_sample()
        audio_buffer.append(sample)
    
    if not audio_buffer:
        return None

    audio_raw = np.concatenate(audio_buffer)
    audio_data = sr.AudioData(audio_raw.tobytes(), 16000, 2)
    
    try:
        text = recognizer.recognize_google(audio_data, language='ko-KR')
        print(f"[인식 결과]: {text}")
        return text
    except:
        return None

# [2단계] 실행부
try:
    with ReachyMini() as mini:
        print("로봇 연결 성공!")
        mini.wake_up()
        speak("반가워요. 명령을 기다리고 있습니다.", mini)
        
        while True:
            command = listen_command(mini)
            if command and "안녕" in command:
                speak("안녕하세요! 저는 리치 미니입니다.", mini)
            elif command and "종료" in command:
                speak("프로그램을 종료합니다.", mini)
                break
            time.sleep(0.5)
except Exception as e:
    print(f"실행 중 오류 발생: {e}")