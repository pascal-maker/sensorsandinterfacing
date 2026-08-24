import os

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO


class ButtonToggle:
    def __init__(self, pin=20, initial=True, bouncetime=300, name="Output"):
        self.pin = pin
        self.enabled = initial
        self.name = name

        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(
            self.pin,
            GPIO.FALLING,
            callback=self._pressed,
            bouncetime=bouncetime,
        )

    def _pressed(self, channel):
        self.enabled = not self.enabled
        print(f"{self.name} {'ON' if self.enabled else 'OFF'}")

    def is_on(self):
        return self.enabled
