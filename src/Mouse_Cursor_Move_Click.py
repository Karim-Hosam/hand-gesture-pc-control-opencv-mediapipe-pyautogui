import pyautogui
import time

class MouseController:
    def __init__(self):
        pyautogui.FAILSAFE = False 
        self.screen_w, self.screen_h = pyautogui.size()
        self.click_times = []
        self.freeze_cursor = False
        self.prev_x, self.prev_y = 0, 0

    def move_cursor(self, index_x, index_y):
        """تحريك مؤشر الماوس"""
        screen_x = int(index_x * self.screen_w)
        screen_y = int(index_y * self.screen_h)
        pyautogui.moveTo(screen_x, screen_y, duration=0.05)
        self.prev_x, self.prev_y = screen_x, screen_y

    def click(self):
        """تنفيذ الضغط (كليك) مفرد أو مزدوج"""
        self.freeze_cursor = True
        self.click_times.append(time.time())
        
        if len(self.click_times) >= 2 and self.click_times[-1] - self.click_times[-2] < 0.4:
            pyautogui.doubleClick()
            self.click_times = []
            return "Double Click"
        else:
            pyautogui.click()
            return "Single Click"

    def scroll(self, amount):
        """عمل سكرول"""
        pyautogui.scroll(amount)

    def take_screenshot(self, filename):
        """أخذ لقطة شاشة"""
        pyautogui.screenshot(filename)