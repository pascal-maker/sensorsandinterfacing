#!/usr/bin/env python3
import cv2
import os

os.makedirs("calibration_images", exist_ok=True)

cap = cv2.VideoCapture(1)
if not cap.isOpened():
    print("Error: could not open webcam")
    exit(1)

count = len(os.listdir("calibration_images"))
print(f"Already have {count} calibration images.")
print("Press 's' to save a frame, 'q' to quit.")
print("Aim at a checkerboard from different angles — target at least 15 images.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    display = frame.copy()
    cv2.putText(display, f"Saved: {count} images | s=save q=quit",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    path = f"calibration_images/frame_{count:03d}.jpg"
    key = input(f"[{count} saved] Press Enter to capture, or type 'q' to quit: ").strip()

    if key == 'q':
        break

    ret, frame = cap.read()
    if ret:
        cv2.imwrite(path, frame)
        print(f"Saved {path}")
        count += 1

cap.release()
print(f"Done. {count} calibration images saved in calibration_images/")
