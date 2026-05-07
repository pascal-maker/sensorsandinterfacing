#!/usr/bin/env python3
import subprocess
import time
from datetime import datetime

import RPi.GPIO as GPIO
from gpiozero import OutputDevice
from mfrc522 import SimpleMFRC522, MFRC522

from basic_lcd import LCDService

BUZZER_PIN  = 12
WEBCAM      = "/dev/video1"
RECORD_SECS = 15

GPIO.setmode(GPIO.BCM)

buzzer = OutputDevice(BUZZER_PIN, active_high=True, initial_value=False)
lcd = LCDService(i2c_addr=0x27)
reader = SimpleMFRC522()
reader.READER = MFRC522(debugLevel='CRITICAL')


def beep(times=1, duration=0.15):
    for i in range(times):
        buzzer.on()
        time.sleep(duration)
        buzzer.off()
        if i < times - 1:
            time.sleep(0.15)


def record_video(filename):
    subprocess.run([
        "ffmpeg", "-y",
        "-f", "v4l2",
        "-input_format", "mjpeg",
        "-t", str(RECORD_SECS),
        "-i", WEBCAM,
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        filename
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def countdown(rfid_id):
    for remaining in range(RECORD_SECS, 0, -1):
        lcd.write("Recording...", f"ID:{rfid_id} {remaining:02d}s")
        time.sleep(1)


try:
    print("Ready. Waiting for RFID scan...")
    while True:
        lcd.write("Place your ID", "to start rec.")

        rfid_id, _ = reader.read()
        rfid_id = str(rfid_id).strip()
        print(f"Card detected: {rfid_id}")

        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        filename = f"{timestamp}_{rfid_id}.mp4"

        beep(1)
        lcd.write("Starting...", f"{filename[:16]}")
        time.sleep(0.5)

        import threading
        record_thread = threading.Thread(target=record_video, args=(filename,))
        record_thread.start()

        countdown(rfid_id)
        record_thread.join()

        beep(2)
        lcd.write("Done!", filename[:16])
        print(f"Saved: {filename}")
        time.sleep(2)

finally:
    lcd.write("Goodbye!", "")
    lcd.cleanup()
    buzzer.close()
    GPIO.cleanup()
