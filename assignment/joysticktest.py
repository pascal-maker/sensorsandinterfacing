#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time

JOY_BUTTON = 7
number = 0

def button_callback(channel):
    global number
    number += 1
    print(f"The joystick has been pressed {number} times!")

GPIO.setmode(GPIO.BCM)
GPIO.setup(JOY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(
    JOY_BUTTON,
    GPIO.FALLING,
    callback=button_callback,
    bouncetime=200
)

print("Joystick button callback test started")
print("Press Ctrl+C to stop")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("\nStopped")