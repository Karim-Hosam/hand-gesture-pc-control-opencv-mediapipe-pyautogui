import time
import cv2
import numpy as np

class ZoomItModeHandler:
    """Handles all gestures when the application is in ZoomIt Mode."""
    def __init__(self, mouse, keyboard):
        self.mouse = mouse
        self.keyboard = keyboard

        self.change_color_cooldown = 1
        self.last_change_color_time = 0
        
        self.zoomit_cooldown = 3
        self.last_zoomit_time = 0
    
        # Track previous point for ZoomIt continuous lines
        self.xp, self.yp = 0, 0
        self.is_dragging = False

    def handle(self, fingers, index_tip, dist_between_thumb_tip_index_pip, is_index_inside_before_box, 
               is_index_inside_after_box, overlay, is_holding_alt, is_canvas_cleared):
        action_text = ""
        if is_holding_alt:
            self.keyboard.release_key('alt')
            is_holding_alt = False
        
        # Clear drawing canvas while in Control Mode
        if not is_canvas_cleared:
            overlay.frameCanvas = np.zeros((720, 1280, 3), np.uint8)
            is_canvas_cleared = True
        
        # Hovering (Index finger only)
        if fingers == [1, 0, 0, 0]:
            self.mouse.move_cursor(index_tip.x, index_tip.y)

            is_pinch = (
                dist_between_thumb_tip_index_pip < 60
                and not (is_index_inside_before_box or is_index_inside_after_box)
            )

            if is_pinch:
                if not self.is_dragging:
                    self.mouse.mouse_down()
                    self.is_dragging = True
                action_text = "ZoomIt Drag"
                return action_text, False, is_holding_alt, is_canvas_cleared
            else:
                if self.is_dragging:
                    self.mouse.mouse_up()
                    self.is_dragging = False
                
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
                    self.keyboard.press_key('b')
                elif overlay.color_in_use_txt == "Green":
                    self.keyboard.press_key('g')
                elif overlay.color_in_use_txt == "Orange":
                    self.keyboard.press_key('o')
                elif overlay.color_in_use_txt == "Purple":
                    self.keyboard.press_key('p')
                elif overlay.color_in_use_txt == "Red":
                    self.keyboard.press_key('r')
                elif overlay.color_in_use_txt == "Yellow":
                    self.keyboard.press_key('y')
                else:
                    self.keyboard.press_key('w')

        # Eraser Selection Mode (Index, Middle, and Ring Fingers)
        elif fingers == [1, 1, 1, 0]:
            current_time = time.time()
            if current_time - self.last_change_color_time > self.change_color_cooldown:
                overlay.is_Eraser_used = True
                overlay.is_Full_Screen_Eraser_used = False
                action_text = "Eraser Used"
                self.last_change_color_time = current_time
                self.mouse.mouse_up()  # Ensure mouse is up before switching to eraser
                self.keyboard.hotkey('ctrl', 'z')
                    
        elif fingers == [1, 1, 1, 1]:
            current_time = time.time()
            if current_time - self.last_change_color_time > self.change_color_cooldown:
                if(not overlay.is_Full_Screen_Eraser_used):
                    overlay.is_Eraser_used = False
                    overlay.is_Full_Screen_Eraser_used = True
                    action_text = "Full Screen Eraser Used"
                    self.last_change_color_time = current_time
                    self.mouse.mouse_up()  # Ensure mouse is up before switching to eraser
                    self.keyboard.press_key('e')  # Assuming 'e' is the eraser shortcut in ZoomIt
            
        
        return action_text, False, is_holding_alt, is_canvas_cleared
