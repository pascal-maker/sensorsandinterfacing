"""
Week 7 — Motors
Classes: DCMotor, StepperMotor
"""

import RPi.GPIO as GPIO#importing the GPIO library
from time import sleep#importing the sleep function


class DCMotor:#DC motor class
    """
    Controls a DC motor via two PWM pins (H-bridge style).
    pin1 driven → forward; pin2 driven → reverse.
    """

    def __init__(self, pin1, pin2, frequency=1000):#initializing the DC motor with the given pin numbers and frequency
        self.pin1 = pin1#setting the pin 1
        self.pin2 = pin2#setting the pin 2
        for pin in (pin1, pin2):#setting the pins to output
            GPIO.setup(pin, GPIO.OUT)
        self._pwm1 = GPIO.PWM(pin1, frequency)#setting the pin 1 as pwm
        self._pwm2 = GPIO.PWM(pin2, frequency)#setting the pin 2 as pwm
        self._pwm1.start(0)#starting the motor pin 1
        self._pwm2.start(0)#starting the motor pin 2

    def forward(self, speed=50):#moving the motor in forward direction
        """Spin forward at speed % (0–100)."""
        speed = max(0, min(100, speed))#setting the speed to be between 0 and 100
        self._pwm1.ChangeDutyCycle(speed)#setting the pin 1 to speed% duty cycle
        self._pwm2.ChangeDutyCycle(0)#setting the pin 2 to 0% duty cycle
        print(f"DC forward  {speed}%")#printing the speed

    def reverse(self, speed=50):#moving the motor in reverse direction
        """Spin in reverse at speed % (0–100)."""
        speed = max(0, min(100, speed))#setting the speed to be between 0 and 100
        self._pwm1.ChangeDutyCycle(0)#setting the pin 1 to 0% duty cycle
        self._pwm2.ChangeDutyCycle(speed)#setting the pin 2 to speed% duty cycle
        print(f"DC reverse  {speed}%")#printing the speed

    def stop(self):#stopping the motor#
        self._pwm1.ChangeDutyCycle(0)#setting the pin 1 to 0% duty cycle
        self._pwm2.ChangeDutyCycle(0)#setting the pin 2 to 0% duty cycle
        print("DC stopped")#printing the speed

    def cleanup(self):#cleaning up the motor#
        self.stop()#stopping the motor
        self._pwm1.stop()#stopping the motor pin 1
        self._pwm2.stop()#stopping the motor pin 2
        del self._pwm1, self._pwm2  # force __del__ now, before GPIO.cleanup()


class StepperMotor:#stepper motor class
    """Controls a 28BYJ-48 style stepper motor using 4 GPIO pins (half-step mode)."""

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

    def __init__(self, pins, step_delay=0.001):#initializing the stepper motor with the given pin numbers and step delay
        if len(pins) != 4:          #checking if the pin numbers are 4
            raise ValueError("StepperMotor requires exactly 4 pins")#raising error if the pin numbers are not 4
        self.pins = pins#setting the pins
        self.step_delay = step_delay#setting the step delay
        GPIO.setup(list(pins), GPIO.OUT)#setting the pins to output

    def _apply_step(self, step):#applying the step to the motor
        for i, pin in enumerate(self.pins):#setting the pins
            GPIO.output(pin, step[i])

    def step_forward(self, steps=512):#rotating the motor in forward direction
        for _ in range(steps):#iterating through the steps
            for step in self.HALF_STEPS:#iterating through the half steps
                self._apply_step(step)#applying the step
                sleep(self.step_delay)#waiting for the step delay

    def step_reverse(self, steps=512):#rotating the motor in reverse direction
        for _ in range(steps):#iterating through the steps
            for step in reversed(self.HALF_STEPS):#iterating through the half steps in reverse order
                self._apply_step(step)#applying the step
                sleep(self.step_delay)#waiting for the step delay

    def release(self):#releasing the motor
        for pin in self.pins:
            GPIO.output(pin, 0)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
if __name__ == "__main__":#demo
    GPIO.setmode(GPIO.BCM)#setting the mode to BCM

    dc = DCMotor(pin1=14, pin2=15)#setting the DC motor with the given pin numbers
    stepper = StepperMotor(pins=(19, 13, 6, 5))#setting the stepper motor with the given pin numbers

    try:
        # DC motor demo
        dc.forward(50)#moving the motor in forward direction
        sleep(3)#waiting for 3 seconds
        dc.reverse(80)#moving the motor in reverse direction
        sleep(3)#waiting for 3 seconds
        dc.stop()#stopping the motor

        # Stepper demo
        print("Stepper forward")#printing the stepper motor forward
        stepper.step_forward(512)#rotating the motor in forward direction
        print("Stepper reverse")#printing the stepper motor reverse
        stepper.step_reverse(512)#rotating the motor in reverse direction

    except KeyboardInterrupt:#keyboard interrupt
        print("Interrupted")#printing the interrupt
    finally:#finally
        dc.cleanup()#cleaning up the motor
        stepper.release()#releasing the motor
        GPIO.cleanup()#cleaning up the motor
