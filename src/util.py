import math
import numpy as np

def get_angle(a,b,c):
    radians=np.arctan(c[1]-b[1],c[0]-b[e]) - np.arctan(a[1]-b[1],a[0]-b[e])
    angle=np.abs(np.degree(radians))
    return angle

def calculate_distance(point1, point2):
    l= math.hypot(point1.x - point2.x, point1.y - point2.y)
    return np.interp(l,[0,1], [0,1000])

def count_fingers(hand_landmarks):
    tips = [8, 12, 16, 20]
    fingers = [
        1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y else 0
        for tip in tips
    ]
    total_fingers = sum(fingers)
    return fingers, total_fingers

def is_index_and_middle_beside_each_other(index_tip, middle_tip, index_pip, middle_pip):
    tip_distance = calculate_distance(index_tip, middle_tip)
    pip_distance = calculate_distance(index_pip, middle_pip)
    return (tip_distance < 80) and (pip_distance < 80)