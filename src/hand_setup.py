import mediapipe as mp

class HandSetup:
    def __init__(self, max_num_hands=1, min_detection_confidence=0.7):
        # Initialize MediaPipe Hands solution and drawing utilities
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Configure hand detection parameters
        self.hands = self.mp_hands.Hands(
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence
        )

    def process_frame(self, rgb_frame):
        # Process the RGB frame to find hand landmarks
        return self.hands.process(rgb_frame)

    def draw_landmarks(self, frame, hand_landmarks):
        # Overlay the detected hand landmarks and connections onto the image
        self.mp_drawing.draw_landmarks(
            frame, 
            hand_landmarks, 
            self.mp_hands.HAND_CONNECTIONS
        )