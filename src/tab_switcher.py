import pyautogui
import time

class TabSwitcher:
    def __init__(self, cooldown=1.0, threshold=0.08):
        # cooldown: ثانية واحدة بين كل تبديلة والتانية عشان ميقلبش كذا تابة ورا بعض
        # threshold: المسافة الأفقية المطلوبة لاعتبار الحركة "سحبة" (نسبة من عرض الشاشة)
        self.cooldown = cooldown
        self.threshold = threshold
        self.last_switch_time = 0
        self.anchor_x = None

    def process_movement(self, current_x):
        current_time = time.time()
        
        # لو لسه في فترة الانتظار (Cooldown)، هنحدث نقطة الارتكاز فقط
        if current_time - self.last_switch_time < self.cooldown:
            self.anchor_x = current_x
            return ""

        # لو دي أول فريم اليد تظهر فيه مفرودة، هنحفظ مكانها كنقطة بداية (Anchor)
        if self.anchor_x is None:
            self.anchor_x = current_x
            return ""

        # حساب الفرق بين الموضع الحالي ونقطة البداية
        dx = current_x - self.anchor_x
        action = ""

        # سحب لليمين (تحريك اليد لليمين)
        if dx > self.threshold:
            pyautogui.hotkey('ctrl', 'tab')  # اختصار الكيبورد للتابة التالية
            action = "Next Tab ->"
            self.last_switch_time = current_time
            self.anchor_x = current_x
        
        # سحب لليسار (تحريك اليد لليسار)
        elif dx < -self.threshold:
            pyautogui.hotkey('ctrl', 'shift', 'tab')  # اختصار الكيبورد للتابة السابقة
            action = "<- Prev Tab"
            self.last_switch_time = current_time
            self.anchor_x = current_x

        return action

    def reset(self):
        """تصفير نقطة البداية لما تقفل إيدك أو تغير وضعها"""
        self.anchor_x = None