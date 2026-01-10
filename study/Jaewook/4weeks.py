import cv2
import time
# 반드시 아래 줄이 포함되어야 ReachyMini를 사용할 수 있습니다
from reachy_mini import ReachyMini 

# 얼굴 인식 모델 로드
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)
last_cmd_time = 0 

# 로봇 연결 및 실행
with ReachyMini() as mini:
    mini.wake_up() # 관절 활성화
    print("실습 시작: 웹캠 창을 보며 고개를 움직여 보세요. (종료: 'q')")
    
    while True:
        ret, frame = cap.read()
        if not ret: 
            break

        # 얼굴 인식 과정
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        if len(faces) > 0:
            # 가장 큰 얼굴 선택 및 좌표 계산
            (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
            cx, cy = x + w // 2, y + h // 2
            
            # 시각화 (웹캠 창에 표시됨)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

            # 0.2초 간격으로 로봇에게 명령 전송
            if time.time() - last_cmd_time > 0.2:
                mini.look_at_image(cx, cy, 0.2)
                last_cmd_time = time.time()

        # [중요] 이 창이 실습 내내 캠 화면을 보여줍니다
        cv2.imshow("Reachy Mini - Face Tracking View", frame)
        
        # 'q' 키를 누르기 전까지 창은 닫히지 않습니다
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()