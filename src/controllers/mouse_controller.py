import pyautogui
import time

class MouseController:
    def __init__(self):
        pyautogui.FAILSAFE = False 
        self.screen_w, self.screen_h = pyautogui.size()
        self.click_times = []
        self.freeze_cursor = False
        self.prev_x, self.prev_y = 0, 0
        self.is_mouse_down = False
        self.smooth_x = None
        self.smooth_y = None

    def move_cursor(self, index_x, index_y, smooth=False):
        screen_x = int(index_x * self.screen_w)
        screen_y = int(index_y * self.screen_h)

        if (screen_x, screen_y) == (self.prev_x, self.prev_y):
            return

        if smooth:
            alpha = 0.35  # lower = smoother, higher = faster
            if self.smooth_x is None:
                self.smooth_x, self.smooth_y = screen_x, screen_y
            else:
                self.smooth_x = int(alpha * screen_x + (1 - alpha) * self.smooth_x)
                self.smooth_y = int(alpha * screen_y + (1 - alpha) * self.smooth_y)

            pyautogui.moveTo(self.smooth_x, self.smooth_y)
            self.prev_x, self.prev_y = self.smooth_x, self.smooth_y
        else:
            pyautogui.moveTo(screen_x, screen_y)
            self.prev_x, self.prev_y = screen_x, screen_y

    def click(self):
        # Freeze the cursor during a click to maintain pointer stability
        self.freeze_cursor = True
        self.click_times.append(time.time())
        
        # Determine if the last two clicks were fast enough to register as a double-click
        if len(self.click_times) >= 2 and self.click_times[-1] - self.click_times[-2] < 0.4:
            pyautogui.doubleClick()
            self.click_times = []
            return "Double Click"
        else:
            pyautogui.click()
            return "Single Click"
        
    def mouse_down(self):
        if not self.is_mouse_down:
            pyautogui.mouseDown()
            self.is_mouse_down = True

    def mouse_up(self):
        if self.is_mouse_down:
            pyautogui.mouseUp()
            self.is_mouse_down = False

    def scroll(self, amount):
        # Scroll the mouse wheel by the given amount
        pyautogui.scroll(amount)

    def take_screenshot(self, filename):
        # Capture and save a screenshot of the primary monitor
        pyautogui.screenshot(filename)
