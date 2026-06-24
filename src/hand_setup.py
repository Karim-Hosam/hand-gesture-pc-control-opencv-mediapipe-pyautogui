import mediapipe as mp

class HandSetup:
    def __init__(self, max_num_hands=1, min_detection_confidence=0.7):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence
        )

    def process_frame(self, rgb_frame):
        return self.hands.process(rgb_frame)

    def draw_landmarks(self, frame, hand_landmarks):
        self.mp_drawing.draw_landmarks(
            frame, 
            hand_landmarks, 
            self.mp_hands.HAND_CONNECTIONS
        )