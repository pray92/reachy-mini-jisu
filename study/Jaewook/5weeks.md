# 1. 가상환경 활성화 확인
.\.venv\Scripts\activate

# 2. 음성 처리 관련 라이브러리 설치
uv pip install gTTS pydub SpeechRecognition numpy

데몬 실행 옵션 변경 (중요!)
지금까지는 에러를 피하기 위해 --deactivate-audio 옵션을 써서 오디오를 껐지만, 5주차부터는 오디오 기능을 켜야 합니다.

터미널 1 (데몬):
PowerShell
# --deactivate-audio 옵션을 제거하고 실행합니다.
.\.venv\Scripts\python.exe -m reachy_mini.daemon.app.main --sim --kinematics-engine AnalyticalKinematics
만약 실행 시 오디오 장치 에러가 난다면, PC의 마이크/스피커가 기본 장치로 잘 설정되어 있는지 확인해 보세요.

import numpy as np
import time
import speech_recognition as sr
from gtts import gTTS
import io
import pydub
from reachy_mini import ReachyMini

def speak(text, mini):
    print(f"[로봇 답변]: {text}")
    tts = gTTS(text=text, lang='ko')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    
    # mp3를 로봇 재생용 데이터로 변환
    audio = pydub.AudioSegment.from_file(fp, format="mp3")
    audio_array = np.array(audio.get_array_of_samples())

    # 로봇의 스피커로 한 조각씩 전달
    chunk_size = 1024
    for i in range(0, len(audio_array), chunk_size):
        chunk = audio_array[i:i+chunk_size]
        mini.media.push_audio_sample(chunk)

def listen_command(mini):
    recognizer = sr.Recognizer()
    print("\n[듣는 중...] 명령을 말씀하세요 (3초)")
    
    audio_buffer = []
    start_time = time.time()
    while time.time() - start_time < 3: # 3초간 녹음
        sample = mini.media.get_audio_sample()
        audio_buffer.append(sample)
    
    audio_raw = np.concatenate(audio_buffer)
    # Reachy Mini 마이크 샘플 레이트 16000Hz, 채널 2(스테레오)
    audio_data = sr.AudioData(audio_raw.tobytes(), 16000, 2)
    
    try:
        text = recognizer.recognize_google(audio_data, language='ko-KR')
        print(f"[인식 결과]: {text}")
        return text
    except:
        print("[오류]: 음성을 인식하지 못했습니다.")
        return None

with ReachyMini() as mini:
    mini.wake_up()
    speak("반가워요. 명령을 기다리고 있습니다.", mini)
    
    while True:
        command = listen_command(mini)
        
        if command:
            if "안녕" in command:
                speak("안녕하세요! 저는 리치 미니입니다.", mini)
            
            elif "고개" in command or "흔들어" in command:
                speak("고개를 흔들어 볼게요.", mini)
                # 고개 끄덕이는 동작 예시
                mini.look_at_image(320, 100, 0.5) # 위
                time.sleep(0.5)
                mini.look_at_image(320, 300, 0.5) # 아래
                time.sleep(0.5)
                mini.look_at_image(320, 240, 0.5) # 정면
            
            elif "종료" in command:
                speak("프로그램을 종료합니다. 다음에 만나요!", mini)
                break
        
        time.sleep(1)


터미널 2에서 python study/Jaewook/5weeks.py를 실행




우리가 사용하는 pydub 라이브러리는 구글에서 받은 MP3 음성 데이터를 로봇이 재생할 수 있는 **숫자 배열(Raw Audio)**로 변환하는 역할을 합니다. 이때 내부적으로 ffmpeg라는 외부 프로그램의 힘을 빌리는데, 현재 컴퓨터에 이 프로그램이 설치되어 있지 않아 "변환을 할 수 없다"고 경고하는 것입니다.

이 상태로 두면 로봇이 인식은 할지 몰라도, 대답(소리 출력)을 할 때 에러가 나며 멈출 가능성이 큽니다.

2. 해결 방법: ffmpeg 설치 (Windows)
가장 빠르고 확실한 해결 방법은 uv를 통해 필요한 바이너리를 가상환경에 추가하는 것입니다.

터미널에서 아래 명령어를 입력해 보세요:

PowerShell

# 가상환경이 활성화된 상태에서 실행
uv pip install ffmpeg-python
만약 위 방법으로도 해결되지 않는다면, 윈도우용 ffmpeg 실행 파일(.exe)이 시스템 경로에 있어야 합니다.


1. 해결 방법: ffmpeg 수동 설치 (Windows 전용)
윈도우 환경에서는 단순히 pip install만으로는 부족할 때가 많습니다. 아래 단계를 따라주세요.

파일 다운로드: gyan.dev 또는 직접 다운로드 링크에서 압축 파일을 받습니다.

압축 해제: 다운로드한 파일의 압축을 풀고, 내부의 bin 폴더 안에 있는 ffmpeg.exe, ffprobe.exe 파일 2개를 복사합니다.

프로젝트 폴더에 붙여넣기: 현재 실습 중인 폴더인 C:\python\reachy-mini-Study\ 폴더 바로 아래에 이 두 파일을 붙여넣으세요. (가장 확실한 방법입니다.)

2. 코드 임시 수정 (경로 강제 지정)
파일을 위와 같이 배치한 후, 5weeks.py의 상단 import 부분 바로 아래에 다음 코드를 추가하여 파이썬이 파일을 확실히 찾도록 설정하세요.

Python

import pydub

# ffmpeg와 ffprobe의 위치를 수동으로 알려줍니다.
# 파일을 프로젝트 루트 폴더에 넣었다면 아래와 같이 설정합니다.
pydub.AudioSegment.converter = r"C:\python\reachy-mini-Study\ffmpeg.exe"
pydub.AudioSegment.ffprobe = r"C:\python\reachy-mini-Study\ffprobe.exe"
3. 소스 코드 구조 재분석: 오디오 엔진의 역할
왜 이 파일들이 꼭 필요한지 흐름도를 통해 다시 확인해 보겠습니다.

gTTS: 구글 서버에서 "압축된" 소리 파일(MP3)을 받아옵니다.

FFmpeg/FFprobe: 이 압축된 파일을 해체(Decoding)하여 컴퓨터가 이해할 수 있는 순수한 숫자 데이터(PCM)로 풀어헤칩니다. (현재 이 단계에서 에러 발생)

Pydub: 풀어헤쳐진 데이터를 파이썬 리스트(Array)로 담아 로봇에게 전달합니다.



#소스 분석 자료#
5주차 오디오 처리 코드는 **"소리 신호(Digital Audio) → 텍스트(STT) → 로직 처리 → 소리 합성(TTS) → 스피커 출력"**의 복잡한 과정을 거칩니다.
 핵심 구간별로 나누어 분석해 드릴게요.

1. 음성 합성 및 출력 (speak 함수)
이 부분은 로봇이 텍스트를 소리로 바꾸어 스피커로 내보내는 과정입니다.

Python

def speak(text, mini):
    # 1. Google TTS를 이용해 텍스트를 MP3 데이터로 변환
    tts = gTTS(text=text, lang='ko')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    
    # 2. pydub를 사용하여 MP3 데이터를 로봇이 처리 가능한 숫자 배열(array)로 변환
    audio = pydub.AudioSegment.from_file(fp, format="mp3")
    audio_array = np.array(audio.get_array_of_samples())

    # 3. 데이터를 청크(Chunk, 작은 조각) 단위로 나누어 로봇 스피커에 밀어넣음
    chunk_size = 1024
    for i in range(0, len(audio_array), chunk_size):
        chunk = audio_array[i:i+chunk_size]
        mini.media.push_audio_sample(chunk)
핵심 포인트: push_audio_sample은 한 번에 큰 데이터를 보낼 수 없으므로, 반복문을 통해 1024 샘플씩 끊어서 실시간 스트리밍하듯 보내야 소리가 끊기지 않습니다.

2. 음성 인식 및 입력 (listen_command 함수)
마이크를 통해 들어오는 미세한 전압 변화(아날로그)를 디지털 데이터로 쌓아 분석하는 과정입니다.

Python

def listen_command(mini):
    # 1. 로봇 마이크로부터 오디오 샘플을 3초 동안 수집
    audio_buffer = []
    start_time = time.time()
    while time.time() - start_time < 3:
        sample = mini.media.get_audio_sample() # 실시간 마이크 데이터 수집
        audio_buffer.append(sample)
    
    # 2. 흩어진 오디오 조각들을 하나로 합침
    audio_raw = np.concatenate(audio_buffer)
    
    # 3. Google이 이해할 수 있는 AudioData 객체로 변환 (16000Hz, 스테레오)
    audio_data = sr.AudioData(audio_raw.tobytes(), 16000, 2)
    
    # 4. Google 서버로 보내 텍스트(String)를 받아옴
    text = recognizer.recognize_google(audio_data, language='ko-KR')
    return text
핵심 포인트: get_audio_sample()은 매우 짧은 순간의 소리 데이터를 가져오기 때문에, while 루프를 사용해 연속적으로 버퍼(Buffer)에 쌓아두는 과정이 반드시 필요합니다.

3. 전체 로직 흐름 (Main Block)
두 기능을 연결하여 로봇의 '행동'을 결정하는 부분입니다.

Python

with ReachyMini() as mini:
    mini.wake_up() # 1. 로봇 관절 모터 활성화
    
    while True:
        command = listen_command(mini) # 2. 듣기
        
        if command: # 3. 판단 및 행동
            if "안녕" in command:
                speak("반가워요!", mini)
            elif "고개" in command:
                mini.look_at_image(320, 100, 0.5) # 4. 동작 수행
💡 실습 시 궁금할 만한 점
샘플 레이트(16000Hz)란?

소리를 초당 16,000번 쪼개서 기록한다는 뜻입니다. 로봇 마이크와 인식 프로그램(Google)의 규격이 일치해야 목소리가 변조되지 않고 정확히 인식됩니다.

왜 np.concatenate를 쓰나요?

마이크 데이터는 [조각1, 조각2, 조각3...] 처럼 리스트에 담겨 있는데, 이를 하나의 긴 소리 파일([조각123...])로 합쳐야 분석이 가능하기 때문입니다.

good!