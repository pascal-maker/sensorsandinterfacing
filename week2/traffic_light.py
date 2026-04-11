"""
Week 2 — Traffic Light
Classes: TrafficLight, PedestrianCrossing
"""

import RPi.GPIO as GPIO
import time


class TrafficLight:
    """Controls a 3-LED traffic light (green / yellow / red)."""

    def __init__(self, pin_green, pin_yellow, pin_red):
        self.green = pin_green
        self.yellow = pin_yellow
        self.red = pin_red
        for pin in (pin_green, pin_yellow, pin_red):
            GPIO.setup(pin, GPIO.OUT)
        self.all_off()

    def _set(self, green, yellow, red):
        GPIO.output(self.green,  GPIO.HIGH if green  else GPIO.LOW)
        GPIO.output(self.yellow, GPIO.HIGH if yellow else GPIO.LOW)
        GPIO.output(self.red,    GPIO.HIGH if red    else GPIO.LOW)

    def show_green(self):
        self._set(True, False, False)

    def show_yellow(self):
        self._set(False, True, False)

    def show_red(self):
        self._set(False, False, True)

    def all_off(self):
        self._set(False, False, False)

    def run_cycle(self, green_time=5, yellow_time=1, red_time=4):
        """Run one full green → yellow → red → off cycle."""
        print("GREEN")
        self.show_green()
        time.sleep(green_time)

        print("YELLOW")
        self.show_yellow()
        time.sleep(yellow_time)

        print("RED")
        self.show_red()
        time.sleep(red_time)

        self.all_off()


class PedestrianCrossing(TrafficLight):
    """Traffic light with a pedestrian request button."""

    def __init__(self, pin_green, pin_yellow, pin_red, pin_button):
        super().__init__(pin_green, pin_yellow, pin_red)
        self.button_pin = pin_button
        GPIO.setup(pin_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self._prev_btn = GPIO.input(pin_button)

    def _button_pressed(self):
        current = GPIO.input(self.button_pin)
        pressed = self._prev_btn == GPIO.HIGH and current == GPIO.LOW
        self._prev_btn = current
        return pressed

    def run(self, green_time=5, yellow_time=1, red_time=4):
        """
        Normal loop: green for green_time seconds.
        If pedestrian button pressed during green, cut green short
        and switch immediately.
        """
        while True:
            self.show_green()
            print("Cars: GREEN")
            start = time.time()
            pedestrian_waiting = False

            while time.time() - start < green_time:
                if self._button_pressed():
                    print("Pedestrian request!")
                    pedestrian_waiting = True
                    break
                time.sleep(0.05)

            print("Cars: YELLOW")
            self.show_yellow()
            time.sleep(yellow_time)

            print("Cars: RED — pedestrians cross" if pedestrian_waiting else "Cars: RED")
            self.show_red()
            time.sleep(red_time)

            self._prev_btn = GPIO.input(self.button_pin)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)

    crossing = PedestrianCrossing(
        pin_green=9, pin_yellow=10, pin_red=11, pin_button=21
    )

    try:
        crossing.run()
    except KeyboardInterrupt:
        print("Exiting")
    finally:
        GPIO.cleanup()
