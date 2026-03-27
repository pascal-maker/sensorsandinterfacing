import RPi.GPIO as GPIO
import time

# Use BCM numbering, so GPIO14 and GPIO15 mean the BCM pin numbers
GPIO.setmode(GPIO.BCM)

# These 2 GPIO pins control the L293D motor driver
motorPin1 = 14
motorPin2 = 15

# Set both motor control pins as OUTPUT pins
GPIO.setup(motorPin1, GPIO.OUT)
GPIO.setup(motorPin2, GPIO.OUT)

# Create a PWM signal on motorPin1 with frequency 1000 Hz
pwm1 = GPIO.PWM(motorPin1, 1000)

# Start PWM on motorPin1 with 0% duty cycle = OFF
pwm1.start(0)

# Create a PWM signal on motorPin2 with frequency 1000 Hz
pwm2 = GPIO.PWM(motorPin2, 1000)

# Start PWM on motorPin2 with 0% duty cycle = OFF
pwm2.start(0)

try:
    # ---- First movement ----
    # motorPin1 gets PWM at 50%
    # motorPin2 stays at 0%
    # Result: motor turns in one direction at medium speed
    print("Direction 1 at 50% speed")
    pwm1.ChangeDutyCycle(50)
    pwm2.ChangeDutyCycle(0)
    time.sleep(3)

    # ---- Second movement ----
    # motorPin1 stays at 0%
    # motorPin2 gets PWM at 80%
    # Result: motor turns in the opposite direction at faster speed
    print("Direction 2 at 80% speed")
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(80)
    time.sleep(3)

    # ---- Third movement ----
    # motorPin1 gets PWM at 30%
    # motorPin2 stays at 0%
    # Result: motor turns back in the first direction, but slower
    print("Direction 1 at 30% speed")
    pwm1.ChangeDutyCycle(30)
    pwm2.ChangeDutyCycle(0)
    time.sleep(3)

    # Stop motor by setting both sides to 0%
    print("Motor stopped")
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)

except KeyboardInterrupt:
    # If you stop the program with Ctrl+C, also stop the motor safely
    print("Program stopped by user")
    pwm1.ChangeDutyCycle(0)
    pwm2.ChangeDutyCycle(0)

finally:
    # Stop the PWM signals completely
    pwm1.stop()
    pwm2.stop()

    # Reset all GPIO pins
    GPIO.cleanup()

#PWM means Pulse Width Modulation.

#It is a way to control how much power a device gets by turning the signal:

#ON
#OFF
#ON
#OFF

#very fast.    PWM is a fast ON/OFF signal used to control the average power going to something like a motor, LED, or buzzer