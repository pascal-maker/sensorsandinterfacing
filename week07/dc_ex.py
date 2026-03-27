import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

motoRPin1 = 14 #left motor
motoRPin2 = 15 #right motor

#set pins to output mode
GPIO.setup(motoRPin1, GPIO.OUT)#output pins pi can send signals
GPIO.setup(motoRPin2, GPIO.OUT)#output pins pi can send signals
dc_pwm_1 = GPIO.PWM(motoRPin1, 1000)#is creates a PWM object on pin 14 with a frequency of 1000 Hz on the left motor.


dc_pwm_1.start(0)#starts the PWM signal on pin 14 with a duty cycle of 0% (off)
dc_pwm_2 = GPIO.PWM(motoRPin2, 1000)#is creates a PWM object on pin 15 with a frequency of 1000 Hz on the right motor.
dc_pwm_2.start(0)#starts the PWM signal on pin 15 with a duty cycle of 0% (off)

#turn left 50%speed
dc_pwm_1.ChangeDutyCycle(50)#changes the duty cycle of the PWM signal on pin 14 to 50%
dc_pwm_2.ChangeDutyCycle(0)#changes the duty cycle of the PWM signal on pin 15 to 0%
time.sleep(3)


#turn left 30%speed
dc_pwm_2.ChangeDutyCycle(30)#changes the duty cycle of the PWM signal on pin 15 to 30%
dc_pwm_1.ChangeDutyCycle(0)#changes the duty cycle of the PWM signal on pin 14 to 0%
time.sleep(3)

dc_pwm_1.stop()#stops the PWM signal on pin 14
dc_pwm_2.stop()#stops the PWM signal on pin 15
del dc_pwm_1#deletes the PWM object on pin 14
del dc_pwm_2#deletes the PWM object on pin 15
GPIO.cleanup()#cleans up the GPIO pins