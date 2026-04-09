import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

LED = 17#set the led as output
GPIO.setup(LED, GPIO.OUT)#set the frequency of the pwm
pwm_led = GPIO.PWM(LED, 1000)#start the pwm with 50% duty cycle
pwm_led.start(50)   # start at 50%

time.sleep(2)#wait for 2 seconds

pwm_led.ChangeDutyCycle(25)   # 25% brightness
time.sleep(2)

pwm_led.ChangeDutyCycle(75)   # 75% brightness
time.sleep(2)#wait for 2 seconds

pwm_led.stop()#stop the pwm
GPIO.cleanup()#cleanup the gpio