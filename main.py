import cv2
import sys
from src.hand_setup import HandSetup
from src.controllers import MouseController
from src.gestures import GestureDetector
from src.overlay import OverlayManager

def main():
    print("\n[INFO] Hand Mouse Control Started...")
    
    # Initialize core controller and configuration modules
    hand_setup = HandSetup()
    mouse_controller = MouseController()
    gesture_detector = GestureDetector(mouse_controller)
    overlay = OverlayManager()
    frame_id = 0  # Initialize frame counter for processing control
    
    # Start video capture from the default webcam
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    if not cap.isOpened():
        print("Cannot open camera")
        sys.exit()

    # Configure the display window to float in the top-right corner
    window_name = overlay.setup_window_fixed_float_top_right_corner()
 
    # Main application loop
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
            
        frame_id = (frame_id + 1) % 1000  # Reset frame_id every 1000 frames to avoid overflow
        
        # Flip the frame horizontally for a natural mirror effect
        frame = cv2.flip(frame, 1) 
        
        # Process every frame, or every 2nd frame if you need more speed
        should_process = (frame_id % 2 == 0)

        if should_process:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect hands in the current frame
            result = hand_setup.process_frame(rgb)
            
            if result.multi_hand_landmarks:
                for hand_landmarks in result.multi_hand_landmarks:
                    # Draw the hand skeleton on the frame
                    hand_setup.draw_landmarks(frame, hand_landmarks)
                    
                    # Determine and perform actions based on the current hand gesture
                    action_text = gesture_detector.detect_and_perform(hand_landmarks, overlay, frame)

                    # Show an on-screen status message for the detected action
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

            # Draw the overlay text notification
            overlay.draw(frame)

            # Apply overlay UI elements (mode selectors, color buttons) to the frame 
            overlay.setup_overlay_mode_color_eraser(frame)
            
            # Merge the drawing canvas layer with the live camera feed
            frame = overlay.setup_overlay_drawing_frame(frame)  
            
            cv2.imshow(window_name, frame)

            # Exit the application when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    # Clean up resources on exit
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()