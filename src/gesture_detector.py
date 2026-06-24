import time
from src.math_util import calculate_distance, count_fingers
from src.tab_switcher import TabSwitcher

class GestureDetector:
    def __init__(self, mouse_controller):
        self.mouse = mouse_controller
        self.screenshot_cooldown = 2
        self.last_screenshot_time = 0
        
        # تهيئة كلاس التابات
        self.tab_switcher = TabSwitcher()

    def detect_and_perform(self, hand_landmarks):
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        
        # استخدام المعصم (Wrist) كنقطة ارتكاز أدق لحركة اليد بالكامل
        wrist_x = hand_landmarks.landmark[0].x 
        
        fingers, total_fingers = count_fingers(hand_landmarks)
        action_text = ""

        # ==========================================
        # أ. وضع السكرين شوت (السبابة والخنصر مفرودين فقط)
        # ==========================================
        if fingers == [1, 0, 0, 1]:
            self.tab_switcher.reset() # تصفير حركة التابات
            current_time = time.time()
            if current_time - self.last_screenshot_time > self.screenshot_cooldown:
                filename = f"screenshot_{int(current_time)}.png"
                self.mouse.take_screenshot(filename)
                print(f"Saved: {filename}")
                self.last_screenshot_time = current_time
                action_text = "Screenshot Taken!"

        # ==========================================
        # ب. وضع تبديل التابات (السبابة والوسطى مفرودين فقط)
        # fingers = [السبابة, الوسطى, البنصر, الخنصر]
        # ==========================================
        elif fingers == [1, 1, 0, 0]:
            tab_action = self.tab_switcher.process_movement(wrist_x)
            if tab_action:
                action_text = tab_action

        # ==========================================
        # ج. وضع الـ Scroll (4 أصابع مفرودة)
        # ==========================================
        elif total_fingers == 4:
            self.tab_switcher.reset() # تصفير حركة التابات
            if index_tip.y < 0.4:
                self.mouse.scroll(60)
                action_text = "Scroll Up"
            elif index_tip.y > 0.6:
                self.mouse.scroll(-60)
                action_text = "Scroll Down"

        # ==========================================
        # د. وضع التحريك والكليك (الأوضاع الأخرى)
        # ==========================================
        else:
            self.tab_switcher.reset() # تصفير حركة التابات
            
            dist = calculate_distance(thumb_tip, index_tip)
            
            # نظام الكليك
            if dist < 0.04:
                action_text = self.mouse.click()
            else:
                self.mouse.freeze_cursor = False
            
            # نظام التحريك
            if not self.mouse.freeze_cursor and (index_tip.x < thumb_tip.x or fingers[0] == 1):
                self.mouse.move_cursor(index_tip.x, index_tip.y)

        return action_text