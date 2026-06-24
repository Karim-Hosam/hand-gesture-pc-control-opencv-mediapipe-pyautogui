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
        wrist_x = hand_landmarks.landmark[0].x 
        
        fingers, total_fingers = count_fingers(hand_landmarks)
        action_text = ""
        
        # حساب المسافة للكليك أولاً
        dist = calculate_distance(thumb_tip, index_tip)

        # ==========================================
        # 1. نظام الكليك (تلامس السبابة والإبهام)
        # ==========================================
        if dist < 0.04:
            self.tab_switcher.reset()
            action_text = self.mouse.click()
            return action_text
        else:
            self.mouse.freeze_cursor = False

        # ==========================================
        # 2. وضع السكرين شوت (السبابة والخنصر فقط)
        # ==========================================
        if fingers == [1, 0, 0, 1]:
            self.tab_switcher.reset() 
            current_time = time.time()
            if current_time - self.last_screenshot_time > self.screenshot_cooldown:
                filename = f"screenshot_{int(current_time)}.png"
                self.mouse.take_screenshot(filename)
                print(f"Saved: {filename}")
                self.last_screenshot_time = current_time
                action_text = "Screenshot Taken!"

        # ==========================================
        # 3. وضع تبديل التابات (السبابة والوسطى فقط)
        # ==========================================
        elif fingers == [1, 1, 0, 0]:
            tab_action = self.tab_switcher.process_movement(wrist_x)
            if tab_action:
                action_text = tab_action

        # ==========================================
        # 4. وضع الـ Scroll (4 أصابع مفرودة)
        # ==========================================
        elif total_fingers == 4:
            self.tab_switcher.reset() 
            if index_tip.y < 0.4:
                self.mouse.scroll(60)
                action_text = "Scroll Up"
            elif index_tip.y > 0.6:
                self.mouse.scroll(-60)
                action_text = "Scroll Down"

        # ==========================================
        # 5. وضع التحريك (السبابة فقط مفرودة)
        # ==========================================
        elif fingers == [1, 0, 0, 0]:
            self.tab_switcher.reset() 
            if not self.mouse.freeze_cursor:
                self.mouse.move_cursor(index_tip.x, index_tip.y)

        # ==========================================
        # 6. وضع الخمول (أي شكل إيد تاني)
        # ==========================================
        else:
            self.tab_switcher.reset() 

        return action_text