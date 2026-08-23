"""Reusable GPIO drivers for the Week 07 stepper and DC motors."""

import time

import RPi.GPIO as GPIO


class StepperMotor:
    """Drive a four-wire 28BYJ-48 stepper through a ULN2003 board."""

    # Moving forward or backward through these eight coil patterns determines
    # the direction. Half-stepping gives smoother, more precise movement.
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

    def __init__(self, pins=(19, 13, 6, 5), step_delay=0.002):
        # Pin order must match ULN2003 inputs IN1, IN2, IN3, and IN4.
        self.pins = tuple(pins)
        # A delay lets the rotor physically respond before the next pattern.
        self.step_delay = step_delay
        self._step_index = 0
        # Begin with all four motor coils switched off.
        GPIO.setup(self.pins, GPIO.OUT, initial=GPIO.LOW)

    def step(self, direction=1):
        """Move one half-step; direction must be 1 (right) or -1 (left)."""
        if direction not in (-1, 1):
            raise ValueError("Stepper direction must be 1 or -1")
        # Modulo wraps the sequence at either end of the tuple.
        self._step_index = (self._step_index + direction) % len(self.HALF_STEPS)
        # Pair each GPIO pin with its value in the selected coil pattern.
        for pin, value in zip(self.pins, self.HALF_STEPS[self._step_index]):
            GPIO.output(pin, value)
        time.sleep(self.step_delay)

    def turn_steps(self, steps, direction=1):
        """Move a fixed number of half-steps and then release the coils."""
        for _ in range(max(0, int(steps))):
            self.step(direction)
        self.release()

    def turn_degrees(self, degrees):
        """Turn approximately the requested number of geared-shaft degrees."""
        direction = 1 if degrees >= 0 else -1
        # A geared 28BYJ-48 requires about 4096 half-steps per full revolution.
        steps = round(abs(degrees) * 4096 / 360)
        self.turn_steps(steps, direction)

    def release(self):
        """Switch off all coils so the motor does not remain energized."""
        GPIO.output(self.pins, GPIO.LOW)

    close = release
    cleanup = release


class DCMotor:
    """Control one DC motor through two L293D H-bridge input pins."""

    OFF = "OFF"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    STATES = (OFF, LEFT, RIGHT)

    def __init__(self, left_pin=14, right_pin=15, frequency=1000):
        self.left_pin = left_pin
        self.right_pin = right_pin
        self.speed = 0.0
        self.state = self.OFF
        # These outputs control opposite sides of the L293D H-bridge.
        GPIO.setup((left_pin, right_pin), GPIO.OUT, initial=GPIO.LOW)
        # PWM changes the average motor voltage to control its speed.
        self._left_pwm = GPIO.PWM(left_pin, frequency)
        self._right_pwm = GPIO.PWM(right_pin, frequency)
        self._left_pwm.start(0)
        self._right_pwm.start(0)

    def set_speed(self, speed):
        """Set and apply a speed from 0 through 100 percent."""
        # Clamp the value because GPIO duty cycle cannot exceed 0..100%.
        self.speed = max(0.0, min(100.0, float(speed)))
        self._apply()

    def set_state(self, state):
        """Select OFF, LEFT, or RIGHT and immediately update the outputs."""
        state = str(state).upper()
        if state not in self.STATES:
            raise ValueError("DC motor state must be OFF, LEFT, or RIGHT")
        self.state = state
        self._apply()

    def toggle(self):
        """Advance through OFF -> LEFT -> RIGHT -> OFF."""
        # Find the current state, move one position, and wrap after RIGHT.
        index = (self.STATES.index(self.state) + 1) % len(self.STATES)
        self.set_state(self.STATES[index])
        return self.state

    def _apply(self):
        # Only one H-bridge input receives PWM at a time. Swapping the active
        # input reverses the voltage polarity and therefore the direction.
        left_duty = self.speed if self.state == self.LEFT else 0
        right_duty = self.speed if self.state == self.RIGHT else 0
        self._left_pwm.ChangeDutyCycle(left_duty)
        self._right_pwm.ChangeDutyCycle(right_duty)

    def stop(self):
        self.set_state(self.OFF)

    def close(self):
        self.stop()
        self._left_pwm.stop()
        self._right_pwm.stop()

    cleanup = close
