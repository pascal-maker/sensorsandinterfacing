"""Active-low push button using the Raspberry Pi internal pull-up resistor."""

import RPi.GPIO as GPIO


class Button:
    def __init__(self, pin, bouncetime=200):
        self.pin = pin
        self.bouncetime = bouncetime
        self._event_registered = False
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    @property
    def is_pressed(self):
        return GPIO.input(self.pin) == GPIO.LOW

    def when_pressed(self, callback):
        """Call callback(button) once for each debounced button press."""
        def gpio_callback(_channel):
            callback(self)

        if self._event_registered:
            GPIO.remove_event_detect(self.pin)
        GPIO.add_event_detect(
            self.pin,
            GPIO.FALLING,
            callback=gpio_callback,
            bouncetime=self.bouncetime,
        )
        self._event_registered = True

    def close(self):
        if self._event_registered:
            GPIO.remove_event_detect(self.pin)
            self._event_registered = False

    cleanup = close
