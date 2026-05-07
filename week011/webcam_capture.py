#!/usr/bin/env python3
import cv2

cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Error: could not open webcam")
    exit(1)

print("Capturing 1 frame and saving to captured_frame.jpg...")

ret, frame = cap.read()
if ret:
    cv2.imwrite("captured_frame.jpg", frame)
    print(f"Saved! Resolution: {frame.shape[1]}x{frame.shape[0]}")
else:
    print("Failed to grab frame")

cap.release()
