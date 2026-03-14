# reachy mini 개발환경

## 1.Reachy Mini Platform

**Choose your platform to access the specific guide:**

| **🤖 Reachy Mini (Wireless)** | **🔌 Reachy Mini Lite** | **💻 Simulation** |
| --- | --- | --- |
| The full autonomous experience.Raspberry Pi 4 + Battery + WiFi. | The developer version.USB connection to your computer. | No hardware required.Prototype in MuJoCo. |
|  |  |  |

![시뮬레이션과 실제 로봇 비교.png](%EC%8B%9C%EB%AE%AC%EB%A0%88%EC%9D%B4%EC%85%98%EA%B3%BC_%EC%8B%A4%EC%A0%9C_%EB%A1%9C%EB%B4%87_%EB%B9%84%EA%B5%90.png)

# ****

## 2-1. Python환경설치

**Git LFS (Large File Storage):**

- 3D 모델(메쉬 파일)을 다운로드하기 위해 필수입니다.
- [git-lfs.com](https://git-lfs.com/)에서 윈도우용 인스톨러를 받아 설치하세요.
- 설치 후 터미널에서 `git lfs install`을 한 번 입력해 줍니다

UV 통한 파이썬 설치 가상환경 설정

```
# 1. uv 설치 (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 2. 프로젝트 디렉토리 생성
mkdir reachy_mini_project
cd reachy_mini_project

# 3. Python 3.12 환경 생성
uv venv --python 3.12

# 4. 가상환경 활성화 (Windows)
.venv\Scripts\activate

# You should see (reachy_mini_env) at the start of your command line prompt!

```

### **2-2. Reachy Mini SDK , Mujoco설치**

> ***Recommended for most users - Just want to control your robot? This is for you!***
> 

실물 로봇 실행 할 경우

```
uv pip install "reachy-mini"
```

Simulation 경우

```
uv pip install "reachy-mini[mujoco]"
```

## 2-3. 로봇 서버 러닝 (Daemon)

The **Daemon** is a background service that handles the low-level communication with motors and sensors. It must be running for your code to work.

# reachy-mini는 ROS가 아니라 gRPC 기반 Deamon이 제어 하는 구조

```
reachy-mini-daemon 
```

- **For Simulation (No robot needed)**
    - **Linux & Windows:**
        
        Copied
        
        ```
        reachy-mini-daemon --sim
        ```
        
    - **macOS:**
        
        Copied
        
        ```
        python -m reachy_mini.daemon.app.main --sim
        ```
        

## **5. Connecting your Code**

Once the simulation is running, it behaves exactly like a real **Reachy Mini Lite** connected via USB. The daemon listens on `localhost`, and you can run any Python SDK script without modification:

```
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# Connects to the simulation running on localhost
with ReachyMini() as mini:
    print("Connected to simulation!")

    # Look up and tilt head
    print("Moving head...")
    mini.goto_target(
        head=create_head_pose(z=20, roll=10, mm=True, degrees=True),
        duration=1.0
    )

    # Wiggle antennas
    print("Wiggling antennas...")
    mini.goto_target(antennas=[0.6, -0.6], duration=0.3)
    mini.goto_target(antennas=[-0.6, 0.6], duration=0.3)

    # Reset to rest position
    mini.goto_target(
        head=create_head_pose(),
        antennas=[0, 0],
        duration=1.0
    )
```

## 

![리치 미니 소프트웨어 스택 다이어그램.png](%EB%A6%AC%EC%B9%98_%EB%AF%B8%EB%8B%88_%EC%86%8C%ED%94%84%ED%8A%B8%EC%9B%A8%EC%96%B4_%EC%8A%A4%ED%83%9D_%EB%8B%A4%EC%9D%B4%EC%96%B4%EA%B7%B8%EB%9E%A8.png)