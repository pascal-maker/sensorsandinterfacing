import RPi.GPIO as GPIO      # import the GPIO library
from time import sleep       # import sleep so we can pause the program

GPIO.setmode(GPIO.BCM)       # use BCM numbering for the GPIO pins

buzzer_pin = 12              # the buzzer is connected to GPIO 12

GPIO.setup(buzzer_pin, GPIO.OUT)   # set GPIO 12 as an output pin

buzzer_pwm = GPIO.PWM(buzzer_pin, 200)   # create PWM on GPIO 12 with frequency 200 Hz

buzzer_pwm.start(10)         # start PWM with duty cycle 10%
sleep(3)                     # keep this for 3 seconds

buzzer_pwm.ChangeDutyCycle(80)   # change duty cycle to 80%
sleep(3)                         # keep this for 3 seconds

buzzer_pwm.ChangeFrequency(400)  # change frequency to 400 Hz
sleep(3)                         # keep this for 3 seconds

buzzer_pwm.ChangeDutyCycle(100)  # change duty cycle to 100%
sleep(3)                         # keep this for 3 seconds

buzzer_pwm.stop()           # stop the PWM signal
GPIO.output(buzzer_pin, 0)  # make sure the buzzer pin is LOW
GPIO.cleanup()              # reset all GPIO pins