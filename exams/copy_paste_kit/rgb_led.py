"""PWM helpers for single LEDs and the Freenove common-anode RGB LED."""

from RPi import GPIO


class PWMLed:
    """Control one LED output with a PWM duty cycle from 0 to 100 percent."""

    def __init__(self, pin, frequency=1000, initial_duty=0):
        self.pin = pin
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, frequency)
        self.pwm.start(self._limit(initial_duty, 0, 100))

    @staticmethod
    def _limit(value, minimum, maximum):
        return max(minimum, min(maximum, value))

    def set_duty(self, percent):
        """Set the raw PWM duty cycle."""
        self.pwm.ChangeDutyCycle(self._limit(percent, 0, 100))

    def stop(self):
        self.pwm.stop()


class RGBLed:
    """Control a common-anode RGB LED with three values from 0 to 255."""

    def __init__(
        self,
        red_pin=5,
        green_pin=6,
        blue_pin=13,
        *,
        frequency=1000,
        maximum_duty=95,
    ):
        # For a common-anode LED, 100% duty means completely off. Keeping the
        # maximum below 100 lets system_off() leave the RGB LED faintly lit.
        self.maximum_duty = PWMLed._limit(maximum_duty, 0, 100)
        self.red = PWMLed(red_pin, frequency, self.maximum_duty)
        self.green = PWMLed(green_pin, frequency, self.maximum_duty)
        self.blue = PWMLed(blue_pin, frequency, self.maximum_duty)
        self.channels = (self.red, self.green, self.blue)

    def _value_to_duty(self, value):
        """Convert brightness 0-255 to inverted common-anode PWM duty."""
        value = PWMLed._limit(value, 0, 255)
        inverted_duty = 100 - value * 100 / 255
        return min(inverted_duty, self.maximum_duty)

    def set_color(self, red, green, blue):
        """Set independent red, green, and blue brightness values (0-255)."""
        for channel, value in zip(self.channels, (red, green, blue)):
            channel.set_duty(self._value_to_duty(value))

    def system_off(self):
        """Set every segment to its faint-glow state instead of fully off."""
        for channel in self.channels:
            channel.set_duty(self.maximum_duty)

    def stop(self):
        """Stop all three PWM controllers before GPIO cleanup."""
        for channel in self.channels:
            channel.stop()
