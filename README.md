# Hand Gesture PC Control ✋💻

A Computer Vision-based application that allows you to control your PC, draw on your screen, and interact with presentation tools entirely through hand gestures. 

Powered by **OpenCV** for live video processing and UI rendering, **MediaPipe** for real-time hand landmark detection, and **PyAutoGUI** for simulating system-level mouse and keyboard actions.

---

## 🚀 Features

- **Multi-Mode System:** Seamlessly switch between Control Mode, Drawing Mode, ZoomIt Mode, and Off Mode using a virtual floating UI.
- **System Control:** Move the cursor, click, scroll, switch tabs, and take screenshots using intuitive hand gestures.
- **On-Screen Drawing:** Draw directly on a transparent canvas overlay with customizable colors and an eraser tool.
- **Presentation Integration:** Natively hooks into the ZoomIt workflow for screen annotation, undoing strokes, and cycling colors on the fly.
- **Floating UI:** A dynamic, non-intrusive top-right overlay displaying active modes, colors, tools, and temporary status notifications.

---

## ⚙️ How It Works

The application operates on a clean, frame-by-frame processing pipeline:

1. **Webcam Capture:** `OpenCV` continuously captures frames from your default webcam.
2. **Landmark Detection:** Frames are processed by `MediaPipe` to identify 21 3D hand landmarks in real-time.
3. **Gesture Classification:** Custom utility functions compute distances (e.g., thumb tip to index PIP joint) and angles to determine which fingers are extended.
4. **Action Routing:** The `GestureDetector` evaluates the hand shape and routes it to the currently active mode handler (`ControlModeHandler`, `DrawingModeHandler`, or `ZoomItModeHandler`).
5. **System Execution:** Mode handlers trigger system-level events (mouse movement, clicks, keyboard shortcuts) via dedicated controller classes, while the `OverlayManager` composites the UI and drawing canvas onto the live video feed.

---

## 🎮 Modes & Controls

You can switch modes by "pinching" (touching your thumb to your index finger) over the **<** or **>** virtual buttons on the top-right overlay window.

### 🖱️ Control Mode
Interact with your operating system normally.

| Gesture | Action |
| :--- | :--- |
| **Index Finger Extended** | Move the cursor |
| **Pinch (Thumb to Index PIP)** | Click |
| **Index + Pinky Extended** | Take a screenshot (saved to the `/screenshots` folder) |
| **Index + Middle Extended** | Switch tabs (Alt + Tab) |
| **4 Fingers Extended** | Scroll up or down (based on hand height) |

### 🎨 Drawing Mode
Draw freely on a transparent overlay canvas.

| Gesture | Action |
| :--- | :--- |
| **Index Finger Extended** | Hover / Preview brush position |
| **Pinch (Thumb to Index PIP)** | Draw continuous strokes |
| **Index + Pinky Extended** | Cycle brush colors |
| **Index + Middle + Ring** | Select Eraser |
| **4 Fingers Extended** | Select Eraser & Clear the entire canvas |

### 🔍 ZoomIt Mode
Automatically triggers the ZoomIt workflow for presentations.

| Gesture | Action |
| :--- | :--- |
| **Index Finger Extended** | Move the cursor |
| **Pinch (Thumb to Index PIP)** | Draw / Hold interaction |
| **Index + Pinky Extended** | Cycle brush colors |
| **Index, Middle, Ring** | Undo last stroke (Ctrl + Z) |
| **4 Fingers Extended** | Clear all ZoomIt drawings |

### ⏸️ Off Mode
- Clears the canvas, escapes ZoomIt if active, and pauses all gesture-based system interactions.

---

## 📂 Project Structure

```text
├── main.py                     # Main application loop and entry point
├── img/                        # UI assets (mode icons, color buttons, etc.)
├── screenshots/                # Automatically generated directory for screenshots
└── src/
    ├── hand_setup.py           # MediaPipe initialization and drawing logic
    ├── util.py                 # Math helpers (distance, angles, finger counting)
    ├── controllers/            # System interaction (MouseController, KeyboardController)
    ├── gestures/               # Gesture routing and mode handlers
    └── overlay/                # UI rendering, asset loading, and canvas management
```

---

## 🛠️ Usage / Getting Started

1. **Install Dependencies:**
   Ensure you have Python installed, then install the required libraries:
   ```bash
   pip install opencv-python mediapipe pyautogui numpy
   ```

2. **Run the Application:**
   ```bash
   python main.py
   ```
   *Note: Ensure your webcam is connected and accessible.*

3. **Interact:**
   A floating window will appear in the top right of your screen. Raise your hand in front of the camera to begin!