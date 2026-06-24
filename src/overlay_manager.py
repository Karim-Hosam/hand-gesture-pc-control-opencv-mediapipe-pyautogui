import time
import cv2

class OverlayManager:
    def __init__(self):
        self.text = ""
        self.color = (255, 255, 255)
        self.until = 0

    def show(self, text, color=(255, 255, 255), duration=1):
        self.text = text
        self.color = color
        self.until = time.time() + duration

    def draw(self, frame):
        if not self.text:
            return

        if time.time() > self.until:
            self.text = ""
            return

        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1.0
        thickness = 2

        (text_w, text_h), baseline = cv2.getTextSize(
            self.text, font, font_scale, thickness
        )

        x, y = 20, 50
        pad_x, pad_y = 14, 12

        box_x1 = x
        box_y1 = y - text_h - pad_y
        box_x2 = x + text_w + 2 * pad_x
        box_y2 = y + baseline + pad_y // 2

        # background box
        cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (25, 25, 25), -1)

        # border
        cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), self.color, 2)

        # text
        cv2.putText(
            frame,
            self.text,
            (x + pad_x, y),
            font,
            font_scale,
            self.color,
            thickness,
            cv2.LINE_AA
        )