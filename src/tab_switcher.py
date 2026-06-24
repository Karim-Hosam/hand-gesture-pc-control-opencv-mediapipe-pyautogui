import pyautogui
import time

class TabSwitcher:
    def __init__(self, cooldown=1.2, threshold=0.03):
        self.cooldown = cooldown
        self.threshold = threshold
        self.last_switch_time = 0
        self.anchor_x = None

    def process_movement(self, current_x):
        current_time = time.time()
        
        if current_time - self.last_switch_time < self.cooldown:
            self.anchor_x = current_x 
            return ""

        if self.anchor_x is None:
            self.anchor_x = current_x
            return ""

        dx = current_x - self.anchor_x
        
        if dx > self.threshold:
            pyautogui.hotkey('ctrl', 'tab')
            self.last_switch_time = current_time
            self.anchor_x = current_x
            return "Next Tab ->"
        
        elif dx < -self.threshold:
            pyautogui.hotkey('ctrl', 'shift', 'tab')
            self.last_switch_time = current_time
            self.anchor_x = current_x
            return "<- Prev Tab"

        return ""

    def reset(self):
        self.anchor_x = None