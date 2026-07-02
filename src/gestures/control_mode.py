import os
import time
import numpy as np
from src.util import is_index_and_middle_beside_each_other

class ControlModeHandler:
    """Handles all gestures when the application is in Control Mode."""
    def __init__(self, mouse, keyboard):
        self.mouse = mouse
        self.keyboard = keyboard
    
        self.screenshot_cooldown = 2
        self.last_screenshot_time = 0

    def handle(self, fingers, total_fingers, index_tip, middle_tip, index_pip, middle_pip, dist_between_thumb_tip_index_pip, 
               is_index_inside_before_box, is_index_inside_after_box, is_holding_alt, overlay):
        action_text = ""
            
        # ==========================================
        # 1. Clicking System (Thumb and Index Finger Touching)
        # ==========================================
        if dist_between_thumb_tip_index_pip < 40 and not (is_index_inside_before_box or is_index_inside_after_box):
            if is_holding_alt:
                self.keyboard.release_key('alt')
                is_holding_alt = False
            action_text = self.mouse.click()
            return action_text, True, is_holding_alt
        else:
            self.mouse.freeze_cursor = False

        # ==========================================
        # 2. Screenshot Mode (Index and Pinky Fingers Only)
        # ==========================================
        if fingers == [1, 0, 0, 1]:
            if is_holding_alt:
                self.keyboard.release_key('alt')
                is_holding_alt = False
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
                if not is_holding_alt:
                    self.keyboard.hold_key('alt')
                    is_holding_alt = True
                self.keyboard.press_key('tab')

        # ==========================================
        # 4. Scroll Mode (4 Fingers Extended)
        # ==========================================
        elif total_fingers == 4:
            if is_holding_alt:
                self.keyboard.release_key('alt')
                is_holding_alt = False
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
            if is_holding_alt:
                self.keyboard.release_key('alt')
                is_holding_alt = False
            if not self.mouse.freeze_cursor:
                self.mouse.move_cursor(index_tip.x, index_tip.y)
            
        # ==========================================
        # 6. Idle Mode (Any Other Hand Shape)
        # ==========================================
        else:
            if is_holding_alt:
                self.keyboard.release_key('alt')
                is_holding_alt = False
        
        return action_text, False, is_holding_alt
