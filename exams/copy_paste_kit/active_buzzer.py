import os
import time

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO


class ActiveBuzzer:
    """On/off active buzzer helper."""

    def __init__(self, pin=23, active_high=True):
        self.pin = pin
        self.on_level = GPIO.HIGH if active_high else GPIO.LOW
        self.off_level = GPIO.LOW if active_high else GPIO.HIGH
        GPIO.setup(pin, GPIO.OUT, initial=self.off_level)

    def on(self):
        GPIO.output(self.pin, self.on_level)

    def off(self):
        GPIO.output(self.pin, self.off_level)

    def beep(self, duration=0.15, count=1, gap=0.1):
        for index in range(max(0, int(count))):
            self.on()
            time.sleep(duration)
            self.off()
            if index + 1 < count:
                time.sleep(gap)

    def cleanup(self):
        self.off()
