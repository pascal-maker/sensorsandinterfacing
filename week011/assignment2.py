#!/usr/bin/env python3
"""
Gesture recognition using OpenCV skin detection + convex hull.
Detects: fist, 1-5 fingers.
- GPIO17: blue LED on when gesture detected
- LED matrix: shows pattern for detected gesture
- Gradio: live camera feed with gesture overlay, accessible on the network
"""
import cv2
import numpy as np
import threading
import time
from collections import deque

import gradio as gr
from shiftregister import ShiftRegister
from ledmatrixclass import LEDMatrix8x8

WEBCAM = 0

PATTERNS = {
    "fist": [
        0b00111100,
        0b01111110,
        0b01111110,
        0b01111110,
        0b01111110,
        0b00111100,
        0b00000000,
        0b00000000,
    ],
    "1": [
        0b00011000,
        0b00011000,
        0b00011000,
        0b00011000,
        0b00011000,
        0b00011000,
        0b00000000,
        0b00000000,
    ],
    "2": [
        0b00100100,
        0b00100100,
        0b00100100,
        0b00100100,
        0b00100100,
        0b00100100,
        0b00000000,
        0b00000000,
    ],
    "3": [
        0b00101100,
        0b00101100,
        0b00101100,
        0b00101100,
        0b00101100,
        0b00101100,
        0b00000000,
        0b00000000,
    ],
    "4": [
        0b01001010,
        0b01001010,
        0b01001010,
        0b01001010,
        0b01001010,
        0b01001010,
        0b00000000,
        0b00000000,
    ],
    "5": [
        0b01010101,
        0b01010101,
        0b01010101,
        0b01010101,
        0b01010101,
        0b01010101,
        0b00000000,
        0b00000000,
    ],
    "none": [0x00] * 8,
}


def count_fingers(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 20, 70], dtype=np.uint8)
    upper = np.array([20, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower, upper)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=4)
    mask = cv2.GaussianBlur(mask, (5, 5), 100)

    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return -1

    cnt = max(contours, key=cv2.contourArea)
    if cv2.contourArea(cnt) < 3000:
        return -1

    hull = cv2.convexHull(cnt, returnPoints=False)
    if hull is None or len(hull) < 3:
        return 0

    try:
        defects = cv2.convexityDefects(cnt, hull)
    except cv2.error:
        return 0

    if defects is None:
        return 0

    fingers = 0
    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(cnt[s][0])
        end   = tuple(cnt[e][0])
        far   = tuple(cnt[f][0])
        a = np.linalg.norm(np.array(end) - np.array(start))
        b = np.linalg.norm(np.array(far) - np.array(start))
        c = np.linalg.norm(np.array(end) - np.array(far))
        angle = np.arccos(np.clip((b**2 + c**2 - a**2) / (2 * b * c), -1, 1))
        if angle <= np.pi / 2 and d > 10000:
            fingers += 1

    return min(fingers + 1, 5)


class MatrixDisplay(threading.Thread):
    def __init__(self, matrix):
        super().__init__(daemon=True)
        self._matrix = matrix
        self._pattern = PATTERNS["none"]
        self._lock = threading.Lock()
        self._running = True

    def set_pattern(self, name):
        with self._lock:
            self._pattern = PATTERNS.get(name, PATTERNS["none"])

    def run(self):
        while self._running:
            with self._lock:
                self._matrix.setPattern(self._pattern)
            self._matrix.refresh_once()

    def stop(self):
        self._running = False


# Shared state between gesture loop and Gradio
_state = {"gesture": "none", "frame": None, "lock": threading.Lock()}


def gesture_loop(cap, sr, display):
    history = deque(maxlen=5)  # smoothing: majority vote over last 5 frames

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        roi = frame[100:400, 100:400]
        fingers = count_fingers(roi)
        raw = "none" if fingers < 0 else ("fist" if fingers == 0 else str(fingers))
        history.append(raw)

        # majority vote for stability
        gesture = max(set(history), key=history.count)

        with _state["lock"]:
            prev = _state["gesture"]
            _state["gesture"] = gesture

            # annotate frame for Gradio
            annotated = frame.copy()
            cv2.rectangle(annotated, (100, 100), (400, 400), (0, 255, 0), 2)
            cv2.putText(annotated, f"Gesture: {gesture}", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
            _state["frame"] = cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB)

        if gesture != prev:
            print(f"Gesture: {gesture}")
            display.set_pattern(gesture)

        time.sleep(0.05)


def stream_feed():
    while True:
        with _state["lock"]:
            frame = _state["frame"]
        if frame is not None:
            yield frame
        time.sleep(0.05)


def get_gesture():
    with _state["lock"]:
        return _state["gesture"]


def main():
    cap = cv2.VideoCapture(WEBCAM)
    if not cap.isOpened():
        print("Cannot open webcam")
        return

    sr = ShiftRegister()
    matrix = LEDMatrix8x8(sr, common_anode=True)
    display = MatrixDisplay(matrix)
    display.start()

    thread = threading.Thread(target=gesture_loop, args=(cap, sr, display), daemon=True)
    thread.start()

    with gr.Blocks(title="Gesture Recognition") as demo:
        gr.Markdown("# Hand Gesture Recognition")
        with gr.Row():
            feed = gr.Image(label="Camera Feed", streaming=True)
            label = gr.Textbox(label="Detected Gesture", value="none")
        btn = gr.Button("Start Stream")
        btn.click(fn=stream_feed, outputs=feed)
        timer = gr.Timer(value=0.5)
        timer.tick(fn=get_gesture, outputs=label)

    try:
        demo.launch(server_name="0.0.0.0", server_port=7860)
    finally:
        display.stop()
        cap.release()
        sr.clear()
        sr.close()


if __name__ == "__main__":
    main()
