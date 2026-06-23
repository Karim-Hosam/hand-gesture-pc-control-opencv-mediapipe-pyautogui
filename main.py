import cv2
import mediapipe as mp
import pyautogui
import time
from src.math_util import get_angle, get_distance
from src.Mouse_Cursor_Move_Click import Mouse_Cursor_Move_Click
from src.hand_setup import hands, mp_drawing, mp_hands

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
        Mouse_Cursor_Move_Click(frame, thumb_tip, index_tip, freeze_cursor, click_times, click_cooldown, screen_w, screen_h)
                        
    cv2.imshow('Live Video', frame)
    if cv2.waitKey(1) == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()