import os
import time

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO


class Keypad4x4:
    """Poll a 4x4 active-low matrix keypad and return debounced key presses."""

    DEFAULT_KEYS = (
        ("1", "2", "3", "A"),
        ("4", "5", "6", "B"),
        ("7", "8", "9", "C"),
        ("*", "0", "#", "D"),
    )

    def __init__(
        self,
        row_pins=(16, 20, 21, 26),
        column_pins=(19, 13, 6, 5),
        keys=DEFAULT_KEYS,
        debounce_seconds=0.04,
    ):
        self.row_pins = tuple(row_pins)
        self.column_pins = tuple(column_pins)
        self.keys = tuple(tuple(row) for row in keys)
        self.debounce_seconds = debounce_seconds
        self.last_key = None
        self.last_change = time.monotonic()

        GPIO.setup(self.row_pins, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.column_pins, GPIO.OUT, initial=GPIO.HIGH)

    def scan(self):
        pressed = None
        for column_index, column_pin in enumerate(self.column_pins):
            GPIO.output(column_pin, GPIO.LOW)
            for row_index, row_pin in enumerate(self.row_pins):
                if GPIO.input(row_pin) == GPIO.LOW:
                    pressed = self.keys[row_index][column_index]
                    break
            GPIO.output(column_pin, GPIO.HIGH)
            if pressed is not None:
                break
        return pressed

    def get_key(self):
        """Return a key once per press, or None while idle/held/bouncing."""
        now = time.monotonic()
        current = self.scan()
        if current != self.last_key:
            if now - self.last_change < self.debounce_seconds:
                return None
            self.last_key = current
            self.last_change = now
            return current
        return None

    def cleanup(self):
        GPIO.output(self.column_pins, GPIO.HIGH)
