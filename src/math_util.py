import math

def calculate_distance(point1, point2):
    """حساب المسافة بين نقطتين"""
    return math.hypot(point1.x - point2.x, point1.y - point2.y)

def count_fingers(hand_landmarks):
    """عد الأصابع المرفوعة (السبابة، الوسطى، البنصر، الخنصر)"""
    tips = [8, 12, 16, 20]
    fingers = [
        1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y else 0
        for tip in tips
    ]
    total_fingers = sum(fingers)
    return fingers, total_fingers