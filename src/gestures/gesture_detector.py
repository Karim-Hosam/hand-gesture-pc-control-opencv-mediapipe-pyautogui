import time
import numpy as np
from src.util import calculate_distance, count_fingers, get_angle
from src.controllers import KeyboardController
from src.gestures.control_mode import ControlModeHandler
from src.gestures.drawing_mode import DrawingModeHandler
from src.gestures.zoomit_mode import ZoomItModeHandler

class GestureDetector:
    def __init__(self, mouse_controller):
        self.mouse = mouse_controller
        self.keyboard = KeyboardController()
        
        # Delegate mode-specific gesture handling to dedicated handlers
        self.control_handler = ControlModeHandler(self.mouse, self.keyboard)
        self.drawing_handler = DrawingModeHandler(self.mouse, self.keyboard)
        self.zoomit_handler = ZoomItModeHandler(self.mouse, self.keyboard)
        # Cooldowns to prevent triggering actions multiple times rapidly
        self.change_mode_cooldown = 0.5
        self.last_change_mode_time = 0
        self.is_in_zoomit_mode = False
        self.is_holding_alt = False
        self.is_canvas_cleared = False
        self.prev_mode = None

    def detect_and_perform(self, hand_landmarks, overlay, frame):
        # Extract key landmarks for easier reference
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        index_pip = hand_landmarks.landmark[6]
        middle_tip = hand_landmarks.landmark[12]
        middle_pip = hand_landmarks.landmark[10]
        pink_tip = hand_landmarks.landmark[20]
        wrist = hand_landmarks.landmark[0]

        
        # print("xp:", self.drawing_handler.xp, "|| yp:", self.drawing_handler.yp)
        
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
            if self.is_holding_alt:
                self.keyboard.release_key('alt')
                self.is_holding_alt = False
            
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
                
        current_mode = overlay.Currnt_Mode_txt

        # clear canvas only when leaving Drawing Mode
        if self.prev_mode == "Drawing Mode" and current_mode != "Drawing Mode":
            overlay.frameCanvas = np.zeros_like(overlay.frameCanvas)
            self.is_canvas_cleared = True

        # when entering Drawing Mode, allow future clear again if needed
        if current_mode == "Drawing Mode":
            self.is_canvas_cleared = False

        self.prev_mode = current_mode
            
        if(overlay.Currnt_Mode_txt == "Control Mode"):
            if self.is_in_zoomit_mode:
                self.mouse.mouse_up()  # Ensure mouse is up before exiting ZoomIt
                self.keyboard.press_key('esc')
                self.is_in_zoomit_mode = False
                
            result, early_return, is_holding_alt = self.control_handler.handle(
                fingers, total_fingers, index_tip, middle_tip, index_pip, middle_pip, dist_between_thumb_tip_index_pip, 
                is_index_inside_before_box, is_index_inside_after_box, self.is_holding_alt, overlay
            )
            self.is_holding_alt = is_holding_alt
            if result:
                action_text = result
            if early_return:
                return action_text
                
        elif overlay.Currnt_Mode_txt == "Drawing Mode":
            if self.is_in_zoomit_mode:
                self.mouse.mouse_up()  # Ensure mouse is up before exiting ZoomIt
                self.keyboard.press_key('esc')
                self.is_in_zoomit_mode = False
                
            result, early_return, is_holding_alt, is_canvas_cleared = self.drawing_handler.handle(
                fingers, index_tip, dist_between_thumb_tip_index_pip, overlay, frame, self.is_holding_alt, self.is_canvas_cleared
            )
            self.is_holding_alt = is_holding_alt
            self.is_canvas_cleared = is_canvas_cleared
            if result:
                action_text = result
            if early_return:
                return action_text
                
        elif overlay.Currnt_Mode_txt == "ZoomIt Mode":
            if not self.is_in_zoomit_mode:
                self.keyboard.hotkey('ctrl', 'shift', '4')
                self.is_in_zoomit_mode = True
                
            result, early_return, is_holding_alt = self.zoomit_handler.handle(
                fingers, index_tip, dist_between_thumb_tip_index_pip, 
                is_index_inside_before_box, is_index_inside_after_box, overlay, self.is_holding_alt
            )
            self.is_holding_alt = is_holding_alt
            if result:
                action_text = result
            if early_return:
                return action_text

        # Off Mode: Clear canvas and do nothing else
        elif overlay.Currnt_Mode_txt == "Off Mode":
            if self.is_in_zoomit_mode:
                self.mouse.mouse_up()  # Ensure mouse is up before exiting ZoomIt
                self.keyboard.press_key('esc')
                self.is_in_zoomit_mode = False
            if not self.is_canvas_cleared:
                overlay.frameCanvas = np.zeros((720, 1280, 3), np.uint8)
                self.is_canvas_cleared = True
                
        return action_text
