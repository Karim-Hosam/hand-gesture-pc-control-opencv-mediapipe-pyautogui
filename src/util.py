import math
import numpy as np

def get_angle(a,b,c):
    # Calculate the angle between three points (a, b, c) using their coordinates
    radians=np.arctan(c.y-b.y,c.x-b.x) - np.arctan(a.y-b.y,a.x-b.x)
    angle=np.abs(np.degree(radians))
    return angle

def calculate_distance(point1, point2):
    # Calculate the Euclidean distance between two points
    l= math.hypot(point1.x - point2.x, point1.y - point2.y)
    
    # Map the normalized distance to a larger scale [0, 1000] for easier thresholding
    return np.interp(l,[0,1], [0,1000])

def count_fingers(hand_landmarks):
    # Landmark indices for the tips of the index, middle, ring, and pinky fingers
    tips = [8, 12, 16, 20]
    
    # Check if each finger is extended by comparing the y-coordinate of the tip 
    # to the y-coordinate of the joint two nodes down
    fingers = [
        1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y else 0
        for tip in tips
    ]
    total_fingers = sum(fingers)
    return fingers, total_fingers

def is_index_and_middle_beside_each_other(index_tip, middle_tip, index_pip, middle_pip):
    # Check if the index and middle fingers are close together at both the tips and the PIP joints
    tip_distance = calculate_distance(index_tip, middle_tip)
    pip_distance = calculate_distance(index_pip, middle_pip)
    return (tip_distance < 80) and (pip_distance < 80)