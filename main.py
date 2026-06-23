import cv2
import mediapipe as mp
from src.util import get_angle, get_distance
import pyautogui
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

click_start_time= None
click_times=[]
click_cooldown=0.5
scroll_mode=False
freeze_cursor=False

screen_w, screen_h = pyautogui.size()

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        ring_tip = hand_landmarks.landmark[16]
        pinky_tip = hand_landmarks.landmark[20]

        fingers = [
            1 if hand_landmarks.landmark[tip].y<hand_landmarks.landmark[tip-2].y else 0
            for tip in [8,12,16,20]
        ]
        
        dist_thumb_index = get_distance([(thumb_tip.x, thumb_tip.y), (index_tip.x, index_tip.y)])
        cv2.putText(frame, f"Distance: {dist_thumb_index:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if dist_thumb_index < 50:
            if not freeze_cursor:
                freeze_cursor=True
                click_times.append(time.time())
                
                if len(click_times) >= 2 and click_times[-1] - click_times[-2] < click_cooldown:
                    pyautogui.doubleClick()
                    cv2.putText(frame, "Double Click", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    click_times = []
                else:
                    pyautogui.click()
                    cv2.putText(frame, "Single Click", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        else:
            freeze_cursor=False  
            
        if not freeze_cursor:
            cursor_x = int(thumb_tip.x * screen_w)
            cursor_y = int(thumb_tip.y * screen_h)
            pyautogui.moveTo(cursor_x, cursor_y, duration=0.05)
                        
    cv2.imshow('Live Video', frame)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()