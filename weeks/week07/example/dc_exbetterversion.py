import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

motorPin1 = 14#left motor   
motorPin2 = 15#right motor

GPIO.setup(motorPin1, GPIO.OUT)#output pins pi can send signals
GPIO.setup(motorPin2, GPIO.OUT)#output pins pi can send signals

pwm1 = GPIO.PWM(motorPin1, 1000)#is creates a PWM object on pin 14 with a frequency of 1000 Hz on the left motor.
pwm2 = GPIO.PWM(motorPin2, 1000)#is creates a PWM object on pin 15 with a frequency of 1000 Hz on the right motor.

pwm1.start(0)#starts the PWM signal on pin 14 with a duty cycle of 0% (off)
pwm2.start(0)#starts the PWM signal on pin 15 with a duty cycle of 0% (off)

try:
    print("Direction 1 at 50% speed")
    pwm1.ChangeDutyCycle(50)#changes the duty cycle of the PWM signal on pin 14 to 50%
    pwm2.ChangeDutyCycle(0)#changes the duty cycle of the PWM signal on pin 15 to 0%
    time.sleep(3)

    print("Direction 2 at 80% speed")
    pwm1.ChangeDutyCycle(0)#changes the duty cycle of the PWM signal on pin 14 to 0%
    pwm2.ChangeDutyCycle(80)#changes the duty cycle of the PWM signal on pin 15 to 80%
    time.sleep(3)

    print("Direction 1 at 30% speed")
    pwm1.ChangeDutyCycle(30)#changes the duty cycle of the PWM signal on pin 14 to 30%
    pwm2.ChangeDutyCycle(0)#changes the duty cycle of the PWM signal on pin 15 to 0%
    time.sleep(3)

    print("Motor stopped")
    pwm1.ChangeDutyCycle(0)#changes the duty cycle of the PWM signal on pin 14 to 0%
    pwm2.ChangeDutyCycle(0)#changes the duty cycle of the PWM signal on pin 15 to 0%

except KeyboardInterrupt:
    print("Program stopped by user")
    pwm1.ChangeDutyCycle(0)#changes the duty cycle of the PWM signal on pin 14 to 0%
    pwm2.ChangeDutyCycle(0)#changes the duty cycle of the PWM signal on pin 15 to 0%

finally:
    pwm1.stop()#stops the PWM signal on pin 14
    pwm2.stop()#stops the PWM signal on pin 15

    pwm1 = None#deletes the PWM object on pin 14
    pwm2 = None#deletes the PWM object on pin 15

    GPIO.cleanup()#cleans up the GPIO pins