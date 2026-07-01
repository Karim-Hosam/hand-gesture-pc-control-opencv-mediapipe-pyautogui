import cv2
import numpy as np


def overlay_png(bg, fg, x, y):
    """Overlays a transparent PNG onto a background image at the given (x,y) coordinates."""
    bh, bw = bg.shape[:2]
    fh, fw = fg.shape[:2]

    # Ignore if the overlay is out of bounds
    if x < 0 or y < 0 or x + fw > bw or y + fh > bh:
        return bg

    # Handle images with an alpha channel
    if fg.shape[2] == 4:
        alpha = fg[:, :, 3] / 255.0
        fg_rgb = fg[:, :, :3]

        for c in range(3):
            bg[y:y+fh, x:x+fw, c] = (
                alpha * fg_rgb[:, :, c] + (1 - alpha) * bg[y:y+fh, x:x+fw, c]
            )
        bg[y:y+fh, x:x+fw] = bg[y:y+fh, x:x+fw].astype(np.uint8)
    else:
        bg[y:y+fh, x:x+fw] = fg

    return bg


class DrawingCanvas:
    """Manages the drawing canvas layer and its compositing with the live feed."""
    def __init__(self):
        self.frameCanvas = np.zeros((480, 640, 3), np.uint8)
    
    def composite(self, frame):
        """Merge the drawing canvas layer with the live webcam feed."""
        h, w = frame.shape[:2]

        # Resize the canvas if the webcam feed size has changed
        if self.frameCanvas.shape[:2] != (h, w):
            self.frameCanvas = np.zeros((h, w, 3), np.uint8)

        # Create an inverted mask of the drawing canvas to poke a hole in the webcam frame
        frameGray = cv2.cvtColor(self.frameCanvas, cv2.COLOR_BGR2GRAY)
        _, frameInv = cv2.threshold(frameGray, 15, 255, cv2.THRESH_BINARY_INV)
        frameInv = cv2.cvtColor(frameInv, cv2.COLOR_GRAY2BGR)

        # Apply the mask and merge the colored canvas drawing on top
        frame = cv2.bitwise_and(frame, frameInv)
        frame = cv2.bitwise_or(frame, self.frameCanvas)

        return frame
