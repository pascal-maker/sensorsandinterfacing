"""
Week 7 — Motors
Classes: DCMotor, StepperMotor
"""

import RPi.GPIO as GPIO
from time import sleep


class DCMotor:
    """
    Controls a DC motor via two PWM pins (H-bridge style).
    pin1 driven → forward; pin2 driven → reverse.
    """

    def __init__(self, pin1, pin2, frequency=1000):
        self.pin1 = pin1
        self.pin2 = pin2
        for pin in (pin1, pin2):
            GPIO.setup(pin, GPIO.OUT)
        self._pwm1 = GPIO.PWM(pin1, frequency)
        self._pwm2 = GPIO.PWM(pin2, frequency)
        self._pwm1.start(0)
        self._pwm2.start(0)

    def forward(self, speed=50):
        """Spin forward at speed % (0–100)."""
        speed = max(0, min(100, speed))
        self._pwm1.ChangeDutyCycle(speed)
        self._pwm2.ChangeDutyCycle(0)
        print(f"DC forward  {speed}%")

    def reverse(self, speed=50):
        """Spin in reverse at speed % (0–100)."""
        speed = max(0, min(100, speed))
        self._pwm1.ChangeDutyCycle(0)
        self._pwm2.ChangeDutyCycle(speed)
        print(f"DC reverse  {speed}%")

    def stop(self):
        self._pwm1.ChangeDutyCycle(0)
        self._pwm2.ChangeDutyCycle(0)
        print("DC stopped")

    def cleanup(self):
        self.stop()
        self._pwm1.stop()
        self._pwm2.stop()


class StepperMotor:
    """
    Controls a unipolar stepper motor via 4 GPIO pins.
    Uses 8-step half-step sequence for smooth movement.
    Default pins: (19, 13, 6, 5) — same as week07/steppermotor.py.
    """

    HALF_STEPS = (
        (1, 0, 0, 0),
        (1, 1, 0, 0),
        (0, 1, 0, 0),
        (0, 1, 1, 0),
        (0, 0, 1, 0),
        (0, 0, 1, 1),
        (0, 0, 0, 1),
        (1, 0, 0, 1),
    )

    def __init__(self, pins, step_delay=0.001):
        if len(pins) != 4:
            raise ValueError("StepperMotor requires exactly 4 pins")
        self.pins = pins
        self.step_delay = step_delay
        GPIO.setup(list(pins), GPIO.OUT)

    def _apply_step(self, step):
        for i, pin in enumerate(self.pins):
            GPIO.output(pin, step[i])

    def step_forward(self, steps=512):
        """Rotate forward by the given number of step cycles."""
        for _ in range(steps):
            for step in self.HALF_STEPS:
                self._apply_step(step)
                sleep(self.step_delay)

    def step_reverse(self, steps=512):
        """Rotate in reverse by the given number of step cycles."""
        for _ in range(steps):
            for step in self.HALF_STEPS:
                self._apply_step(tuple(reversed(step)))
                sleep(self.step_delay)

    def release(self):
        """De-energise all coils."""
        for pin in self.pins:
            GPIO.output(pin, 0)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)

    dc = DCMotor(pin1=14, pin2=15)
    stepper = StepperMotor(pins=(19, 13, 6, 5))

    try:
        # DC motor demo
        dc.forward(50)
        sleep(3)
        dc.reverse(80)
        sleep(3)
        dc.stop()

        # Stepper demo
        print("Stepper forward")
        stepper.step_forward(512)
        print("Stepper reverse")
        stepper.step_reverse(512)

    except KeyboardInterrupt:
        print("Interrupted")
    finally:
        dc.cleanup()
        stepper.release()
        GPIO.cleanup()
