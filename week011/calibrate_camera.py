#!/usr/bin/env python3
import cv2
import numpy as np
import glob
import pickle

CHECKERBOARD = (8, 5)

objp = np.zeros((CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

objpoints = []
imgpoints = []

images = sorted(glob.glob("calibration_images/*.jpg"))
print(f"Found {len(images)} images")

for path in images:
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD,
                   cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_NORMALIZE_IMAGE + cv2.CALIB_CB_FAST_CHECK)
    if ret:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1),
                                    (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001))
        imgpoints.append(corners2)
        print(f"  OK: {path}")
    else:
        print(f"  SKIP (no corners found): {path}")

if len(objpoints) < 5:
    print("Not enough valid images for calibration (need at least 5)")
    exit(1)

print(f"\nCalibrating with {len(objpoints)} valid images...")
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print(f"Reprojection error: {ret:.4f} (lower is better, <1.0 is good)")
print(f"\nCamera matrix:\n{mtx}")
print(f"\nDistortion coefficients:\n{dist}")

with open("calibration.pkl", "wb") as f:
    pickle.dump({"camera_matrix": mtx, "dist_coeffs": dist}, f)
print("\nCalibration saved to calibration.pkl")

img = cv2.imread(images[0])
h, w = img.shape[:2]
new_mtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
undistorted = cv2.undistort(img, mtx, dist, None, new_mtx)
cv2.imwrite("undistorted_sample.jpg", undistorted)
print("Undistorted sample saved to undistorted_sample.jpg")
