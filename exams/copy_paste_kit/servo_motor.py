import os

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO


class ServoMotor:
    """Small 50 Hz hobby-servo helper with angle clamping."""

    def __init__(self, pin=18, minimum_duty=2.5, maximum_duty=12.5):
        self.pin = pin
        self.minimum_duty = minimum_duty
        self.maximum_duty = maximum_duty
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
        self.pwm = GPIO.PWM(pin, 50)
        self.pwm.start(0)

    def angle_to_duty(self, angle):
        angle = max(0, min(180, float(angle)))
        span = self.maximum_duty - self.minimum_duty
        return self.minimum_duty + (angle / 180) * span

    def set_angle(self, angle):
        self.pwm.ChangeDutyCycle(self.angle_to_duty(angle))

    def release(self):
        self.pwm.ChangeDutyCycle(0)

    def cleanup(self):
        self.pwm.stop()
        GPIO.output(self.pin, GPIO.LOW)
