# from main import *
import cv2
import pyautogui
import time
from src.math_util import get_distance
        
def Mouse_Cursor_Move_Click(frame, thumb_tip, index_tip, freeze_cursor, click_times, click_cooldown, screen_w, screen_h):
    dist_thumb_index = get_distance([(thumb_tip.x, thumb_tip.y), (index_tip.x, index_tip.y)])
    cv2.putText(frame, f"Distance: {dist_thumb_index:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    if dist_thumb_index < 50:
        if not freeze_cursor:
            freeze_cursor=True
            click_times.append(time.time())
            
            if len(click_times) >= 2 and click_times[-1] - click_times[-2] < click_cooldown:
                pyautogui.doubleClick()
                cv2.putText(frame, "Double Click", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                click_times = []
            else:
                pyautogui.click()
                cv2.putText(frame, "Single Click", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
    else:
        freeze_cursor=False  
        
    if not freeze_cursor:
        cursor_x = int(thumb_tip.x * screen_w)
        cursor_y = int(thumb_tip.y * screen_h)
        pyautogui.moveTo(cursor_x, cursor_y, duration=0.05)
            
    return frame, freeze_cursor, click_times