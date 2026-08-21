"""
Week 1 — GPIO Basics
Classes: LED, Button
"""

import RPi.GPIO as GPIO
import time


class LED:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)

    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self):
        GPIO.output(self.pin, GPIO.LOW)

    def toggle(self):
        GPIO.output(self.pin, not GPIO.input(self.pin))

    def blink(self, interval=0.5):
        self.toggle()
        time.sleep(interval)


class Button:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self._previous = GPIO.input(pin)

    def is_pressed(self):
        """Return True while button is held down (active-LOW)."""
        return GPIO.input(self.pin) == GPIO.LOW

    def fell(self):
        """Return True on the falling edge (button just pressed)."""
        current = GPIO.input(self.pin)
        edge = self._previous == GPIO.HIGH and current == GPIO.LOW
        self._previous = current
        return edge

    def rose(self):
        """Return True on the rising edge (button just released)."""
        current = GPIO.input(self.pin)
        edge = self._previous == GPIO.LOW and current == GPIO.HIGH
        self._previous = current
        return edge

    def update(self):
        """Call once per loop to keep edge detection state fresh."""
        self._previous = GPIO.input(self.pin)


# ---------------------------------------------------------------------------
# Demo — mirrors toggleassignement.py and multibutton.py behaviour
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)

    led = LED(17)
    btn = Button(20)

    # Four-button multi-mode demo (same pins as week1/multibutton.py)
    btn1 = Button(20)   # LED on
    btn2 = Button(21)   # LED off
    btn3 = Button(16)   # blink fast
    btn4 = Button(26)   # blink slow

    mode = "off"

    try:
        while True:
            if btn1.is_pressed():
                mode = "on"
            elif btn2.is_pressed():
                mode = "off"
            elif btn3.is_pressed():
                mode = "blink_fast"
            elif btn4.is_pressed():
                mode = "blink_slow"

            if mode == "on":
                led.on()
            elif mode == "off":
                led.off()
            elif mode == "blink_fast":
                led.blink(0.1)
            elif mode == "blink_slow":
                led.blink(0.5)

    except KeyboardInterrupt:
        pass
    finally:
        GPIO.cleanup()
