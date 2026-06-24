import os
import time
import cv2
import numpy as np
from src.util import calculate_distance, count_fingers, is_index_and_middle_beside_each_other, get_angle
from src.keyboard_controller import KeyboardController

class GestureDetector:
    def __init__(self, mouse_controller):
        self.mouse = mouse_controller
        self.keyboard = KeyboardController()
        self.screenshot_cooldown = 2
        self.last_screenshot_time = 0
        
        # Drawing mode
        self.prev_draw_point = None
        self.canvas = None  
        

    def detect_and_perform(self, hand_landmarks, frame):
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        middle_tip = hand_landmarks.landmark[12]
        index_pip = hand_landmarks.landmark[6]
        middle_pip = hand_landmarks.landmark[10]
        pink_tip = hand_landmarks.landmark[20]
        wrist = hand_landmarks.landmark[0]
        
        fingers, total_fingers = count_fingers(hand_landmarks)
        action_text = ""
        
        dist = calculate_distance(thumb_tip, index_tip)
        
        # h, w = frame.shape[:2]
        # x, y = int(index_tip.x * w), int(index_tip.y * h)

        # if self.canvas is None or self.canvas.shape != frame.shape:
        #     self.canvas = np.zeros_like(frame)


        # ==========================================
        # 1. Clicking System (Thumb and Index Finger Touching)
        # ==========================================
        if dist < 40:
            self.keyboard.release_key('alt')
            action_text = self.mouse.click()
            return action_text
        else:
            self.mouse.freeze_cursor = False

        # ==========================================
        # 2. Screenshot Mode (Index and Pinky Fingers Only)
        # ==========================================
        if fingers == [1, 0, 0, 1]:
            self.keyboard.release_key('alt')
            current_time = time.time()
            if current_time - self.last_screenshot_time > self.screenshot_cooldown:
                # Create screenshots folder if it doesn't exist
                screenshots_dir = "screenshots"
                os.makedirs(screenshots_dir, exist_ok=True)

                filename = os.path.join(
                    screenshots_dir,
                    f"screenshot_{int(current_time)}.png"
                )

                self.mouse.take_screenshot(filename)
                print(f"Saved: {filename}")
                self.last_screenshot_time = current_time
                action_text = "Screenshot Taken!"

        # ==========================================
        # 3. Tab Switching Mode (Index and Middle Fingers Only)
        # ==========================================
        elif fingers == [1, 1, 0, 0]:
            if is_index_and_middle_beside_each_other(index_tip, middle_tip, index_pip, middle_pip):
                self.keyboard.hold_key('alt')
                self.keyboard.press_key('tab')

        # ==========================================
        # 4. Scroll Mode (4 Fingers Extended)
        # ==========================================
        elif total_fingers == 4:
            self.keyboard.release_key('alt')
            if index_tip.y < 0.4:
                self.mouse.scroll(60)
                action_text = "Scroll Up"
            elif index_tip.y > 0.6:
                self.mouse.scroll(-60)
                action_text = "Scroll Down"

        # ==========================================
        # 5. Cursor Movement Mode (Index Finger Only Extended)
        # ==========================================
        elif fingers == [1, 0, 0, 0]:
            self.keyboard.release_key('alt')
            if not self.mouse.freeze_cursor:
                self.mouse.move_cursor(index_tip.x, index_tip.y)

        #==========================================
        # 6. Drawing Mode (Index and Thumb 90 Degrees)
        #==========================================
        # elif fingers == [1, 0, 0, 0] and get_angle(thumb_tip, wrist, pink_tip) > 90:
        #     self.keyboard.release_key('alt') 
        #     self.mouse.freeze_cursor = True

        #     if self.prev_draw_point is None:
        #         self.prev_draw_point = (index_tip.x, index_tip.y)
        #     else:
        #         cv2.line(self.canvas, self.prev_draw_point, (index_tip.x, index_tip.y), (0, 255, 0), 5)
        #         self.prev_draw_point = (index_tip.x, index_tip.y)

        #     action_text = "Drawing Mode"
            
        # ==========================================
        # 7. Idle Mode (Any Other Hand Shape)
        # ==========================================
        else:
            self.keyboard.release_key('alt')

        return action_text