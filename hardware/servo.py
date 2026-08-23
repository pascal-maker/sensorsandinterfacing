"""PWM driver for a conventional 0-to-180-degree hobby servo."""

import time

import RPi.GPIO as GPIO


class ServoMotor:
    def __init__(
        self,
        pin,
        frequency=50,
        min_pulse_ms=0.5,
        max_pulse_ms=2.5,
    ):
        self.pin = pin
        self.frequency = frequency
        self.min_pulse_ms = min_pulse_ms
        self.max_pulse_ms = max_pulse_ms
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, frequency)
        self.pwm.start(0)

    def angle_to_duty_cycle(self, angle):
        angle = max(0.0, min(180.0, float(angle)))
        pulse_ms = self.min_pulse_ms + (
            angle / 180.0
        ) * (self.max_pulse_ms - self.min_pulse_ms)
        period_ms = 1000.0 / self.frequency
        return pulse_ms / period_ms * 100.0

    def set_angle(self, angle, move_time=0.3, release=True):
        """Move to an angle, optionally releasing PWM afterward to reduce jitter."""
        duty = self.angle_to_duty_cycle(angle)
        self.pwm.ChangeDutyCycle(duty)
        if move_time > 0:
            time.sleep(move_time)
        if release:
            self.release()
        return duty

    def release(self):
        self.pwm.ChangeDutyCycle(0)

    def close(self):
        self.release()
        self.pwm.stop()

    cleanup = close
