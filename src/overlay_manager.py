import time
import cv2
import os
import numpy as np

class OverlayManager:
    def __init__(self):
        # Temporary text display properties
        self.text = ""
        self.color = (255, 255, 255)
        self.until = 0
        
        # Drawing mode configuration
        self.brushThickness = 10
        self.eraserThickness = 100
        self.drawColor = (255, 0, 0)
        self.frameCanvas = np.zeros((480, 640, 3), np.uint8)
        
        self.folderPath = "img"
        self.myList = os.listdir(self.folderPath)
        
        self.ModesList_img = []
        self.ModesList_txt = []
        
        self.Before = []
        self.After = []
        
        self.ColorsList_img = []
        self.ColorsList_txt = []
        self.Eraser = []
        self.ZoomIt_Logo = []
        self.is_in_ZoomIt = False
        self.is_Eraser_used = False
        
        # Categorize loaded images into their respective UI lists
        for imPath in self.myList:
            image = cv2.imread(f'{self.folderPath}/{imPath}', cv2.IMREAD_UNCHANGED)
            
            if "Mode" in imPath:
                self.ModesList_img.append(image)
                self.ModesList_txt.append(imPath.split(".")[0])
            
            elif "Color" in imPath:
                self.ColorsList_img.append(image)
                self.ColorsList_txt.append(imPath.split(" Color")[0])
                
            elif imPath == "Eraser.png":
                self.Eraser.append(image)
                
            elif imPath == "Before.png":
                self.Before.append(image)
                
            elif imPath == "After.png":
                self.After.append(image)
                
            elif imPath == "ZoomIt_Logo.png":
                self.ZoomIt_Logo.append(image)
                
        # Set default active mode and color
        self.Currnt_Mode_index = 0
        self.Currnt_Mode_img = self.ModesList_img[self.Currnt_Mode_index]
        self.Currnt_Mode_txt = self.ModesList_txt[self.Currnt_Mode_index]
        
        self.color_in_use_index = 0
        self.color_in_use_img = self.ColorsList_img[self.color_in_use_index]
        self.color_in_use_txt = self.ColorsList_txt[self.color_in_use_index]            
        
        print("ModesList_txt: ", self.ModesList_txt)
        print("ColorsList_txt: ", self.ColorsList_txt)
        
        # Button positions to be calculated dynamically later
        self.after_btn_x = 0
        self.current_mode_btn_x= 0
        self.before_btn_x = 0

    def show(self, text, color=(255, 255, 255), duration=1):
        # Queue a text message to be displayed on screen for a given duration
        self.text = text
        self.color = color
        self.until = time.time() + duration

    def draw(self, frame):
        # Do not draw if there's no active message or it has expired
        if not self.text:
            return

        if time.time() > self.until:
            self.text = ""
            return

        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 1.0
        thickness = 2

        # Calculate text dimensions to draw a fitted background box
        (text_w, text_h), baseline = cv2.getTextSize(
            self.text, font, font_scale, thickness
        )
    
        h, w = frame.shape[:2]
        x, y = 20, h-50
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
        
    def overlay_png(bg, fg, x, y):
        # Overlays a transparent PNG onto a background image at the given (x,y) coordinates
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
    
    def setup_window_fixed_float_top_right_corner(self):
        # Configure the main display window to sit at the top right of the screen
        window_name = "Hand Control live video"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        small_w = 576
        small_h = 432
        cv2.resizeWindow(window_name, small_w, small_h)
        screen_w = 1920
        x = screen_w - small_w - 10
        y = 10
        cv2.moveWindow(window_name, x, y)
        
        # Keep the window floating above all others
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
        
        return window_name
    
    def setup_overlay_mode_color_eraser(self, frame):
        # Render the mode selection buttons and current active tool icons
        h, w = frame.shape[:2]
        current_mode_h, current_mode_w = self.Currnt_Mode_img.shape[:2]
        bef_aft_h, bef_aft_w = self.Before[0].shape[:2]
        
        # Calculate dynamic positions for top-right mode buttons
        self.after_btn_x = w - bef_aft_w - 10
        self.current_mode_btn_x= self.after_btn_x - current_mode_w   
        self.before_btn_x = self.current_mode_btn_x - bef_aft_w
        frame = OverlayManager.overlay_png(frame, self.After[0], self.after_btn_x, 5)
        frame = OverlayManager.overlay_png(frame, self.Before[0], self.before_btn_x, 5)
        frame = OverlayManager.overlay_png(frame, self.Currnt_Mode_img, self.current_mode_btn_x, 15)
        
        # Display the active tool icon in Drawing Mode
        if(self.Currnt_Mode_txt == "Drawing Mode"):
            if(self.is_in_ZoomIt):
                frame = OverlayManager.overlay_png(frame, self.ZoomIt_Logo[0], 2, 2)
                
            elif(self.is_Eraser_used):
                frame = OverlayManager.overlay_png(frame, self.Eraser[0], 2, 2)
                
            else:
                frame = OverlayManager.overlay_png(frame, self.color_in_use_img, 2, 2)
        
    
    def setup_overlay_drawing_frame(self, frame):
        # Merge the drawing canvas layer with the live webcam feed
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