import pyautogui
import time

class KeyboardController:
    def __init__(self):
        pyautogui.FAILSAFE = False
        self.last_key_time = 0
        self.key_cooldown = 0.4  # Cooldown in seconds

    def press_key(self, key):
        current_time = time.time()
        if current_time - self.last_key_time > self.key_cooldown:
            pyautogui.press(key)
            self.last_key_time = current_time
            return f"Key '{key}' Pressed"
        return ""
    
    def hold_key(self, key):
        pyautogui.keyDown(key)
        return f"Key '{key}' Held Down"
    
    def release_key(self, key):
        pyautogui.keyUp(key)
        return f"Key '{key}' Released"
    