import time
import cv2
import numpy as np

class DrawingModeHandler:
    """Handles all gestures when the application is in Drawing Mode."""
    def __init__(self, mouse, keyboard):
        self.mouse = mouse
        self.keyboard = keyboard

        self.change_color_cooldown = 1
        self.last_change_color_time = 0
        
        self.zoomit_cooldown = 3
        self.last_zoomit_time = 0
    
        # Track previous point for drawing continuous lines
        self.xp, self.yp = 0, 0

    def handle(self, fingers, total_fingers, index_tip,
               dist_between_thumb_tip_index_pip, is_index_inside_before_box, is_index_inside_after_box,
               overlay, frame):
        action_text = ""
        self.keyboard.release_key('alt')
        
        # Hovering (Index finger only)
        if fingers == [1, 0, 0, 0]:
            h, w = frame.shape[:2]
            cx, cy = int(index_tip.x * w), int(index_tip.y * h)
            
            # Draw a preview circle on the index finger tip
            cv2.circle(frame, (cx, cy), 55 if overlay.is_Eraser_used else 10, overlay.drawColor, cv2.FILLED)
            
            action_text = "Drawing Mode"
            
            # Draw on the canvas if thumb and index finger PIP joint are close enough (pinch gesture)
            if dist_between_thumb_tip_index_pip < 60:
                # Reset starting point if we just started drawing
                if self.xp == 0 and self.yp == 0:
                    self.xp, self.yp = cx, cy

                cv2.line(
                    overlay.frameCanvas,
                    (self.xp, self.yp),
                    (cx, cy),
                    overlay.drawColor,
                    overlay.eraserThickness if overlay.is_Eraser_used else overlay.brushThickness
                )

                self.xp, self.yp = cx, cy
            else:
                self.xp, self.yp = 0, 0
                
        # Color Selection Mode (Index and Pinky Fingers)
        elif fingers == [1, 0, 0, 1]:
            current_time = time.time()
            if current_time - self.last_change_color_time > self.change_color_cooldown:
                # Cycle through the available brush colors
                overlay.color_in_use_index = (overlay.color_in_use_index + 1) % len(overlay.ColorsList_img)
                overlay.color_in_use_img = overlay.ColorsList_img[overlay.color_in_use_index]
                overlay.color_in_use_txt = overlay.ColorsList_txt[overlay.color_in_use_index]
                action_text = f"Color Changed to: {overlay.color_in_use_txt}"
                self.last_change_color_time = current_time
                overlay.is_Eraser_used = False
                
                # Apply the selected color to the brush
                if overlay.color_in_use_txt == "Blue":
                    overlay.drawColor = (255, 0, 0)
                elif overlay.color_in_use_txt == "Green":
                    overlay.drawColor = (0, 255, 0)
                elif overlay.color_in_use_txt == "Orange":
                    overlay.drawColor = (0, 165, 255)
                elif overlay.color_in_use_txt == "Purple":
                    overlay.drawColor = (128, 0, 128)
                elif overlay.color_in_use_txt == "Red":
                    overlay.drawColor = (0, 0, 255)
                elif overlay.color_in_use_txt == "Yellow":
                    overlay.drawColor = (0, 255, 255)
                else:
                    overlay.drawColor = (255, 255, 255)
                    
        # Eraser Selection Mode (Index, Middle, and Ring Fingers)
        elif fingers == [1, 1, 1, 0]:
            current_time = time.time()
            if current_time - self.last_change_color_time > self.change_color_cooldown:
                if(not overlay.is_Eraser_used):
                    overlay.is_Eraser_used = True
                    action_text = "Eraser Used"
                    self.last_change_color_time = current_time
                    # Erase by drawing in black, which will be filtered out by bitwise operations
                    overlay.drawColor = (0, 0, 0)
            
        elif fingers == [1, 1, 1, 1]:
            current_time = time.time()
            if current_time - self.last_change_color_time > self.change_color_cooldown:
                if(not overlay.is_Eraser_used):
                    overlay.is_Eraser_used = True
                    action_text = "Eraser Used"
                    self.last_change_color_time = current_time 
                    # Erase by drawing in black, which will be filtered out by bitwise operations
                    overlay.drawColor = (0, 0, 0)      
                    # Clear drawing canvas while in Control Mode
                    overlay.frameCanvas = np.zeros((720, 1280, 3), np.uint8)

        
        return action_text, False
