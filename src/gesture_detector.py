import os
import time
import cv2
import numpy as np
import pyautogui
from src.util import calculate_distance, count_fingers, is_index_and_middle_beside_each_other, get_angle
from src.keyboard_controller import KeyboardController

class GestureDetector:
    def __init__(self, mouse_controller):
        self.mouse = mouse_controller
        self.keyboard = KeyboardController()
        
        # Cooldowns to prevent triggering actions multiple times rapidly
        self.screenshot_cooldown = 2
        self.last_screenshot_time = 0
        
        self.change_color_cooldown = 1
        self.last_change_color_time = 0
        
        self.change_mode_cooldown = 0.5
        self.last_change_mode_time = 0
        
        self.zoomit_cooldown = 3
        self.last_zoomit_time = 0
        
        # Track previous point for drawing continuous lines
        self.xp, self.yp = 0, 0   
        

    def detect_and_perform(self, hand_landmarks, overlay, frame):
        # Extract key landmarks for easier reference
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        index_pip = hand_landmarks.landmark[6]
        middle_tip = hand_landmarks.landmark[12]
        middle_pip = hand_landmarks.landmark[10]
        pink_tip = hand_landmarks.landmark[20]
        wrist = hand_landmarks.landmark[0]

        
        # print("xp:", self.xp, "|| yp:", self.yp)
        
        fingers, total_fingers = count_fingers(hand_landmarks)
        action_text = ""
        
        dist_between_thumb_tip_index_pip = calculate_distance(thumb_tip, index_pip)

        # Create variables to check if the index finger is interacting with the on-screen UI buttons
        h, w = frame.shape[:2]
        bef_aft_h, bef_aft_w = overlay.Before[0].shape[:2]
        is_index_inside_before_box = ((index_tip.x * w > overlay.before_btn_x) and (index_tip.x * w < overlay.before_btn_x + bef_aft_w) and (index_tip.y * h < bef_aft_h + 10))
        is_index_inside_after_box = ((index_tip.x * w > overlay.after_btn_x) and (index_tip.x * w < overlay.after_btn_x + bef_aft_w) and (index_tip.y * h < bef_aft_h + 10))

        # ==========================================
        # 0. Change Mode
        # ==========================================
        if dist_between_thumb_tip_index_pip < 40 and (is_index_inside_before_box or is_index_inside_after_box):
            self.keyboard.release_key('alt')
            
            current_time = time.time()
            if current_time - self.last_change_mode_time > self.change_mode_cooldown:
                # Cycle through the available modes (Control, Drawing, Off)
                if is_index_inside_before_box:
                    overlay.Currnt_Mode_index = (overlay.Currnt_Mode_index - 1) % len(overlay.ModesList_img)
                elif is_index_inside_after_box:
                    overlay.Currnt_Mode_index = (overlay.Currnt_Mode_index + 1) % len(overlay.ModesList_img)
                    
                overlay.Currnt_Mode_img = overlay.ModesList_img[overlay.Currnt_Mode_index]
                overlay.Currnt_Mode_txt = overlay.ModesList_txt[overlay.Currnt_Mode_index]
                action_text = f"Mode Changed to: {overlay.Currnt_Mode_txt}"
                
                self.last_change_mode_time = current_time
            
        if(overlay.Currnt_Mode_txt == "Control Mode"):
            # Clear drawing canvas while in Control Mode
            overlay.frameCanvas = np.zeros((720, 1280, 3), np.uint8)
            # ==========================================
            # 1. Clicking System (Thumb and Index Finger Touching)
            # ==========================================
            if dist_between_thumb_tip_index_pip < 40 and not (is_index_inside_before_box or is_index_inside_after_box):
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
                    # Hold Alt and press Tab to bring up the window switcher
                    self.keyboard.hold_key('alt')
                    self.keyboard.press_key('tab')

            # ==========================================
            # 4. Scroll Mode (4 Fingers Extended)
            # ==========================================
            elif total_fingers == 4:
                self.keyboard.release_key('alt')
                # Scroll based on the vertical position of the hand
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
                
            # ==========================================
            # 7. Idle Mode (Any Other Hand Shape)
            # ==========================================
            else:
                self.keyboard.release_key('alt')
                
        elif overlay.Currnt_Mode_txt == "Drawing Mode":
            self.keyboard.release_key('alt')
            
            # Hovering (Index finger only)
            if fingers == [1, 0, 0, 0]:
                h, w = frame.shape[:2]
                cx, cy = int(index_tip.x * w), int(index_tip.y * h)
                
                # Draw a preview circle on the index finger tip
                cv2.circle(frame, (cx, cy), 10, overlay.drawColor, cv2.FILLED)
                
                action_text = "Drawing Mode"
                
                # Draw on the canvas if thumb and index finger PIP joint are close enough (pinch gesture)
                if dist_between_thumb_tip_index_pip < 60:
                    # Reset starting point if we just started drawing
                    if self.xp == 0 and self.yp == 0:
                        self.xp, self.yp = cx, cy

                    cv2.line(
                        overlay.frameCanvas,
                        (self.xp, self.yp),
                        (cx, cy),
                        overlay.drawColor,
                        overlay.eraserThickness if overlay.is_Eraser_used else overlay.brushThickness
                    )

                    self.xp, self.yp = cx, cy
                else:
                    self.xp, self.yp = 0, 0
                    
            # Color Selection Mode (Index and Pinky Fingers)
            elif fingers == [1, 0, 0, 1]:
                current_time = time.time()
                if current_time - self.last_change_color_time > self.change_color_cooldown:
                    # Cycle through the available brush colors
                    overlay.color_in_use_index = (overlay.color_in_use_index + 1) % len(overlay.ColorsList_img)
                    overlay.color_in_use_img = overlay.ColorsList_img[overlay.color_in_use_index]
                    overlay.color_in_use_txt = overlay.ColorsList_txt[overlay.color_in_use_index]
                    action_text = f"Color Changed to: {overlay.color_in_use_txt}"
                    self.last_change_color_time = current_time
                    overlay.is_Eraser_used = False
                    
                    # Apply the selected color to the brush
                    if overlay.color_in_use_txt == "Blue":
                        overlay.drawColor = (255, 0, 0)
                    elif overlay.color_in_use_txt == "Green":
                        overlay.drawColor = (0, 255, 0)
                    elif overlay.color_in_use_txt == "Orange":
                        overlay.drawColor = (0, 165, 255)
                    elif overlay.color_in_use_txt == "Purple":
                        overlay.drawColor = (128, 0, 128)
                    elif overlay.color_in_use_txt == "Red":
                        overlay.drawColor = (0, 0, 255)
                    elif overlay.color_in_use_txt == "Yellow":
                        overlay.drawColor = (0, 255, 255)
                    else:
                        overlay.drawColor = (255, 255, 255)
                        
            # Eraser Selection Mode (Index, Middle, and Ring Fingers)
            elif fingers == [1, 1, 1, 0]:
                current_time = time.time()
                if current_time - self.last_change_color_time > self.change_color_cooldown:
                    if(not overlay.is_Eraser_used):
                        overlay.is_Eraser_used = True
                        action_text = "Eraser Used"
                        self.last_change_color_time = current_time
                        # Erase by drawing in black, which will be filtered out by bitwise operations
                        overlay.drawColor = (0, 0, 0)
                
            elif fingers == [1, 1, 1, 1]:
                current_time = time.time()
                if current_time - self.last_zoomit_time > self.zoomit_cooldown:
                    overlay.is_in_ZoomIt = True
                    action_text = "ZoomIt Used"
                    pyautogui.hotkey('ctrl', 'shift', '4')
                    self.last_zoomit_time = current_time
            
            # Sub-mode: If we are actively in ZoomIt mode, we can still move the cursor or click
            if overlay.is_in_ZoomIt:
                if fingers == [1, 0, 0, 0]:
                    if not self.mouse.freeze_cursor:
                        self.mouse.move_cursor(index_tip.x, index_tip.y)
                        
                if dist_between_thumb_tip_index_pip < 40 and not (is_index_inside_before_box or is_index_inside_after_box):
                    self.keyboard.release_key('alt')
                    action_text = self.mouse.click()
                    return action_text
                else:
                    self.mouse.freeze_cursor = False
                
        # Off Mode: Clear canvas and do nothing else
        elif overlay.Currnt_Mode_txt == "Off Mode":
            overlay.frameCanvas = np.zeros((720, 1280, 3), np.uint8)
                
        return action_text