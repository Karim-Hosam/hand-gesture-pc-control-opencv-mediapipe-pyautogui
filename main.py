import cv2
import sys
from src.hand_setup import HandSetup
from src.mouse_controller import MouseController
from src.gesture_detector import GestureDetector
from src.overlay_manager import OverlayManager

def main():
    print("\n[INFO] Hand Mouse Control Started...")
    
    hand_setup = HandSetup()
    mouse_controller = MouseController()
    gesture_detector = GestureDetector(mouse_controller)
    overlay = OverlayManager()
    
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Cannot open camera")
        sys.exit()

    window_name = overlay.setup_window_fixed_float_top_right_corner()
 
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
            
        frame = cv2.flip(frame, 1) 
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        result = hand_setup.process_frame(rgb)
        
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                hand_setup.draw_landmarks(frame, hand_landmarks)
                action_text = gesture_detector.detect_and_perform(hand_landmarks, overlay, frame)

                if action_text:
                    if action_text == "Screenshot Taken!":
                        overlay.show(action_text, (255, 255, 0), 1)
                    elif action_text == "Scroll Up":
                        overlay.show(action_text, (0, 255, 0), 1)
                    elif action_text == "Scroll Down":
                        overlay.show(action_text, (0, 0, 255), 1)
                    elif action_text in ["Single Click", "Double Click"]:
                        overlay.show(action_text, (255, 255, 0), 1)
                    elif action_text in ["Next Tab ->", "<- Prev Tab"]:
                        overlay.show(action_text, (255, 0, 255), 1)

        overlay.draw(frame)

        overlay.setup_overlay_mode_color_eraser(frame)
        frame = overlay.setup_overlay_drawing_frame(frame)  
        
        cv2.imshow(window_name, frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()