from __future__ import annotations

from time import sleep

from gpio_compat import GPIO


class ActiveBuzzerService:#Active buzzer service class

    def __init__(self, pin: int) -> None:#Constructor
        self.pin = int(pin)#Set buzzer pin
        GPIO.setwarnings(False)#Turn off warnings
        GPIO.setmode(GPIO.BCM)#Set buzzer mode to BCM
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)#Set buzzer pin to output with low initial value

    def on(self) -> None:##Turn on buzzer
        GPIO.output(self.pin, GPIO.HIGH)#Set buzzer pin to high

    def off(self) -> None:##Turn off buzzer
        GPIO.output(self.pin, GPIO.LOW)

    def beep(self, duration: float = 0.2) -> None:#Beep buzzer for a specified duration
        self.on()#Turn on buzzer
        sleep(duration)#Wait for specified duration
        self.off()

    def cleanup(self) -> None:
        GPIO.output(self.pin, GPIO.LOW)
        GPIO.cleanup(self.pin)


class PassiveBuzzerService:
    """Passive buzzer — needs PWM to generate sound. Controls frequency and duty cycle."""

    def __init__(self, pin: int) -> None:#Constructor
        self.pin = int(pin)#Set buzzer pin
        GPIO.setwarnings(False)#Turn off warnings
        GPIO.setmode(GPIO.BCM)#Set buzzer mode to BCM
        GPIO.setup(self.pin, GPIO.OUT)#Set buzzer pin to output
        self._pwm = GPIO.PWM(self.pin, 440)#Create PWM instance
        self._pwm.start(0)#Start PWM

    def play_tone(self, frequency: float, duration: float, duty: float = 50) -> None:##Play tone
        if frequency <= 0:#Check if frequency is less than or equal to 0
            self._pwm.ChangeDutyCycle(0)#Change duty cycle to 0
            sleep(duration)#Wait for specified duration
            return
        self._pwm.ChangeFrequency(frequency)#Change frequency
        self._pwm.ChangeDutyCycle(duty)#Change duty cycle
        sleep(duration)#Wait for specified duration
        self._pwm.ChangeDutyCycle(0)#Change duty cycle to 0

    def stop(self) -> None:##Stop buzzer
        if self._pwm is not None:#Check if PWM is not None
            self._pwm.ChangeDutyCycle(0)#Change duty cycle to 0

    def cleanup(self) -> None:##Cleanup buzzer
        if self._pwm is not None:#Check if PWM is not None
            self._pwm.ChangeDutyCycle(0)#Change duty cycle to 0
            self._pwm.stop()#Stop PWM
            self._pwm = None
        GPIO.output(self.pin, GPIO.LOW)#Set buzzer pin to low
        GPIO.cleanup(self.pin)#Cleanup buzzer pin
