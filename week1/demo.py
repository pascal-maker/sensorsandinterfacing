import time 
from RPi import GPIO # importing the RPi GPIO library
GPIO.setmode(GPIO.BCM)#define pinnaming /numbering method
btn = 20#we define button
LED = 17# we define led

GPIO.setup(btn,GPIO.IN,pull_up_down=GPIO.PUD_UP)# our btn is input , with a pull up (alwys needed for buttons to read high state when no press)
GPIO.setup(LED,GPIO.OUT)# our led pin is an output and should alwys be conected
try:
    while True:
        value = GPIO.input(btn)# read value of btn and store it in value
        GPIO.output(LED, not value)# write opposite of btn value to the led pin
        print('The value of pin {0} is {1}'.format(btn,value))#verbose print btn pin and value
        time.sleep(0.5)# wait for 0.5 seconds
except KeyboardInterrupt:
    pass   #ignore the keyboard interrupt    

finally:
    GPIO.cleanup()#release the GPIO pins         
       