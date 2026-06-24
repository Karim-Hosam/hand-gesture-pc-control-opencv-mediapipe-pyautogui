import cv2
import sys
from src.hand_setup import HandSetup
from src.Mouse_Cursor_Move_Click import MouseController
from src.gesture_detector import GestureDetector
from src.math_util import calculate_distance, count_fingers
def main():
    print("\n[INFO] Hand Mouse Control Started...")
    
    # تهيئة الكلاسات من الملفات الأخرى
    hand_setup = HandSetup()
    mouse_controller = MouseController()
    gesture_detector = GestureDetector(mouse_controller)
    
    # تشغيل الكاميرا
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        sys.exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1) 
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # معالجة الصورة واكتشاف اليد
        result = hand_setup.process_frame(rgb)
        
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # رسم اليد
                hand_setup.draw_landmarks(frame, hand_landmarks)
                
                # اكتشاف الحركة وتنفيذ الأوامر
                action_text = gesture_detector.detect_and_perform(hand_landmarks)
                
                # طباعة النصوص على الشاشة بناءً على الحركة
                if action_text == "Screenshot Taken!":
                    cv2.putText(frame, action_text, (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
                elif action_text == "Scroll Up":
                    cv2.putText(frame, action_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                elif action_text == "Scroll Down":
                    cv2.putText(frame, action_text, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                elif action_text in ["Single Click", "Double Click"]:
                    cv2.putText(frame, action_text, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        # عرض الفيديو الحي
        cv2.imshow("Hand Control live video", frame)
        
        # الخروج عند الضغط على زر 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()