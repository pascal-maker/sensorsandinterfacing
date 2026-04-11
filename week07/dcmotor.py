import RPi.GPIO as GPIO#importing the GPIO library
import time#importing the time library

GPIO.setmode(GPIO.BCM)#setting the mode to BCM

motorPin1 = 14#setting the motor pin 1
motorPin2 = 15#setting the motor pin 2

GPIO.setup(motorPin1, GPIO.OUT)#setting the motor pin 1 as output
GPIO.setup(motorPin2, GPIO.OUT)#setting the motor pin 2 as output

dc_pwm_1 = GPIO.PWM(motorPin1, 1000)#setting the motor pin 1 as pwm
dc_pwm_1.start(0)#starting the motor pin 1

dc_pwm_2 = GPIO.PWM(motorPin2, 1000)#setting the motor pin 2 as pwm

dc_pwm_2.start(0)#starting the motor pin 2

try:
    dc_pwm_1.ChangeDutyCycle(50)#setting the motor pin 1 to 50% duty cycle
    dc_pwm_2.ChangeDutyCycle(0)#setting the motor pin 2 to 0% duty cycle
    
    print("Motor is running")#printing that the motor is running
    time.sleep(5)#waiting for 5 seconds
    
    
    dc_pwm_1.ChangeDutyCycle(0)#setting the motor pin 1 to 0% duty cycle
    dc_pwm_2.ChangeDutyCycle(80)#setting the motor pin 2 to 80% duty cycle
    print("Motor turning right at 80% speed ")#printing that the motor is turning right at 80% speed
    time.sleep(3)#waiting for 3 seconds
    
    dc_pwm_1.ChangeDutyCycle(30)#setting the motor pin 1 to 30% duty cycle
    dc_pwm_2.ChangeDutyCycle(0)#setting the motor pin 2 to 0% duty cycle
    print("Motor turning left at 30% speed")#printing that the motor is turning left at 30% speed
    time.sleep(3)#waiting for 3 seconds
finally:
    dc_pwm_1.stop()#stopping the motor pin 1
    dc_pwm_2.stop()#stopping the motor pin 2
    GPIO.cleanup()#cleaning up the GPIO
    
    print("Motor stopped, GPIO cleaned up")#printing that the motor is stopped and GPIO is cleaned up