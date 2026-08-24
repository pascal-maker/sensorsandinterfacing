# Two buzzer driver classes — one for each buzzer type used in this project.
#
# ActiveBuzzerService  (GPIO 12)
#   An active buzzer contains its own oscillator circuit.
#   You only need to switch the pin HIGH/LOW — the buzzer generates its own tone.
#   No frequency or duty-cycle control is possible.
#
# PassiveBuzzerService (GPIO 14)
#   A passive buzzer is just a speaker coil with no internal oscillator.
#   It requires an external PWM signal to vibrate and produce sound.
#   Changing the PWM frequency changes the pitch; duty cycle controls drive strength.
from __future__ import annotations

from time import sleep

from .gpio_compat import GPIO  # relative import keeps hardware/ self-contained


class ActiveBuzzerService:
    """Active buzzer — digital ON/OFF only. Has its own internal oscillator."""

    def __init__(self, pin: int) -> None:
        self.pin = int(pin)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)  # start silent

    def on(self) -> None:
        """Switch the buzzer on continuously."""
        GPIO.output(self.pin, GPIO.HIGH)

    def off(self) -> None:
        """Switch the buzzer off."""
        GPIO.output(self.pin, GPIO.LOW)

    def beep(self, duration: float = 0.2) -> None:
        """Emit a single beep of the given duration (seconds)."""
        self.on()
        sleep(duration)
        self.off()

    def cleanup(self) -> None:
        """Silence and release the GPIO pin."""
        GPIO.output(self.pin, GPIO.LOW)
        GPIO.cleanup(self.pin)


class PassiveBuzzerService:
    """Passive buzzer — needs PWM to generate sound. Controls frequency and duty cycle."""

    def __init__(self, pin: int) -> None:
        self.pin = int(pin)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        # Initialise PWM at 440 Hz (concert A) with 0% duty cycle (silent)
        self._pwm = GPIO.PWM(self.pin, 440)
        self._pwm.start(0)

    def play_tone(self, frequency: float, duration: float, duty: float = 50) -> None:
        """Play a tone for `duration` seconds.

        frequency -- pitch in Hz (set to 0 or negative for silence)
        duration  -- how long to play (seconds)
        duty      -- PWM duty cycle 1–99 % (affects drive strength / perceived volume)
        """
        if frequency <= 0:
            # Silence: keep duty at 0 and just wait
            self._pwm.ChangeDutyCycle(0)
            sleep(duration)
            return
        self._pwm.ChangeFrequency(frequency)   # set pitch
        self._pwm.ChangeDutyCycle(duty)         # start driving the coil
        sleep(duration)
        self._pwm.ChangeDutyCycle(0)            # silence after the tone

    def stop(self) -> None:
        """Immediately silence the buzzer without releasing the pin."""
        if self._pwm is not None:
            self._pwm.ChangeDutyCycle(0)

    def cleanup(self) -> None:
        """Silence, stop PWM, and release the GPIO pin."""
        if self._pwm is not None:
            self._pwm.ChangeDutyCycle(0)
            self._pwm.stop()
            self._pwm = None
        GPIO.output(self.pin, GPIO.LOW)
        GPIO.cleanup(self.pin)
