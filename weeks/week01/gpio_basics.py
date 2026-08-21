"""
Week 1 — GPIO Basics
Classes: LED, Button
"""

import RPi.GPIO as GPIO
import time


class LED:
    """Small wrapper around one GPIO output pin connected to an LED."""

    def __init__(self, pin):
        # Remember the BCM pin number so the other methods can reuse it.
        self.pin = pin
        self._is_on = False

        # Configure the pin as an output and start LOW so the LED is off.
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)
        print(f"LED GPIO {self.pin} configured: OFF")

    def on(self):
        """Drive the output HIGH to switch the LED on."""
        if not self._is_on:
            GPIO.output(self.pin, GPIO.HIGH)
            self._is_on = True
            print(f"LED GPIO {self.pin}: ON")

    def off(self):
        """Drive the output LOW to switch the LED off."""
        if self._is_on:
            GPIO.output(self.pin, GPIO.LOW)
            self._is_on = False
            print(f"LED GPIO {self.pin}: OFF")

    def toggle(self):
        """Change the LED from on to off, or from off to on."""
        # GPIO.input() can also read the current level of an output pin.
        self._is_on = not GPIO.input(self.pin)
        GPIO.output(self.pin, self._is_on)
        print(f"LED GPIO {self.pin}: {'ON' if self._is_on else 'OFF'}")

    def blink(self, interval=0.5):
        """Toggle once and wait; repeated calls produce a blinking LED."""
        self.toggle()
        time.sleep(interval)


class Button:
    """Read an active-LOW push button and detect press/release edges."""

    def __init__(self, pin):
        self.pin = pin

        # The internal pull-up holds the input HIGH while the button is open.
        # Connecting the button to ground makes the input LOW when pressed.
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        print(f"Button GPIO {self.pin} configured with pull-up")

        # Save the initial state for later edge comparisons.
        self._previous = GPIO.input(pin)

    def is_pressed(self):
        """Return True while button is held down (active-LOW)."""
        return GPIO.input(self.pin) == GPIO.LOW

    def fell(self):
        """Return True on the falling edge (button just pressed)."""
        current = GPIO.input(self.pin)

        # A falling edge is the transition HIGH -> LOW. With a pull-up input,
        # that transition means the user has just pressed the button.
        edge = self._previous == GPIO.HIGH and current == GPIO.LOW
        self._previous = current
        return edge

    def rose(self):
        """Return True on the rising edge (button just released)."""
        current = GPIO.input(self.pin)

        # A rising edge is the transition LOW -> HIGH, meaning release.
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
    # BCM numbering refers to GPIO numbers, not physical header pin numbers.
    GPIO.setmode(GPIO.BCM)

    # The LED is connected to GPIO 17.
    led = LED(17)

    # A basic button object for experimenting with is_pressed/fell/rose.
    btn = Button(20)

    # Four-button multi-mode demo (same pins as week1/multibutton.py)
    btn1 = Button(20)   # LED on
    btn2 = Button(21)   # LED off
    btn3 = Button(16)   # blink fast
    btn4 = Button(26)   # blink slow

    mode = "off"
    previous_mode = None

    print("Demo started. Press Ctrl+C to stop safely.")
    print("GPIO 20=ON | GPIO 21=OFF | GPIO 16=FAST | GPIO 26=SLOW")

    try:
        while True:
            # A button press selects a mode. The selected mode remains active
            # after the button is released because it is stored in `mode`.
            if btn1.is_pressed():
                mode = "on"
            elif btn2.is_pressed():
                mode = "off"
            elif btn3.is_pressed():
                mode = "blink_fast"
            elif btn4.is_pressed():
                mode = "blink_slow"

            # Print only when the selected mode changes.
            if mode != previous_mode:
                print(f"Mode: {previous_mode or 'startup'} -> {mode}")
                previous_mode = mode

            # Perform the action belonging to the currently selected mode.
            if mode == "on":
                led.on()
            elif mode == "off":
                led.off()
            elif mode == "blink_fast":
                led.blink(0.1)
            elif mode == "blink_slow":
                led.blink(0.5)

    except KeyboardInterrupt:
        # Ctrl+C is the normal way to stop this continuously running demo.
        print("\nCtrl+C received. Stopping the demo...")
    finally:
        # Always restore the GPIO pins, even if the program is interrupted.
        GPIO.cleanup()
        print("GPIO cleanup complete. Program ended safely.")
