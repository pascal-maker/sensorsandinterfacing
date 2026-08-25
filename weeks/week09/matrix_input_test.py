"""Test raw controls while continuously refreshing the LED matrix."""

import threading
import time

import RPi.GPIO as GPIO

from led_matrix import LedMatrix8x8
from shift_register import ShiftRegister


PINS = {
    "UP": 20,
    "DOWN": 21,
    "LEFT": 26,
    "RIGHT": 16,
    "JOY": 7,
}


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    for pin in PINS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    matrix = LedMatrix8x8(ShiftRegister())
    stop_display = threading.Event()

    def refresh_display():
        while not stop_display.is_set():
            matrix.refresh_once(3, 3, True)

    display_thread = threading.Thread(target=refresh_display, daemon=True)
    display_thread.start()

    print("Matrix + input test started")
    print("A fixed centre LED should be visible. Press every control once.")
    print("Each pressed control must change from 1 to 0 and back to 1.")
    print("Press Ctrl+C to stop.")
    previous = None

    try:
        while True:
            current = {name: GPIO.input(pin) for name, pin in PINS.items()}
            if current != previous:
                print(" ".join(f"{name}={value}" for name, value in current.items()))
                previous = current
            time.sleep(0.005)
    except KeyboardInterrupt:
        print("\nMatrix + input test stopped")
    finally:
        stop_display.set()
        display_thread.join(timeout=1)
        matrix.blank()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
