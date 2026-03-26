import time 
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

LED1 = 9
LED2 = 10

LED3 = 11

BUTTON1 = 20


GPIO.setup(LED1,GPIO.OUT)
GPIO.setup(LED2,GPIO.OUT)
GPIO.setup(LED3,GPIO.OUT)

GPIO.setup(BUTTON1,GPIO.IN,pull_up_down=GPIO.PUD_UP)


#start with all lights off
GPIO.output(LED1,GPIO.LOW)
GPIO.output(LED2,GPIO.LOW)
GPIO.output(LED3,GPIO.LOW)

#start with all lights off

try:
    while True:
        current_button1_state = GPIO.input(BUTTON1)

        if current_button1_state == GPIO.LOW:
           GPIO.output(LED1,GPIO.HIGH)
           GPIO.output(LED2,GPIO.LOW)
           GPIO.output(LED3,GPIO.LOW)
           print("GReen trafic light")
           time.sleep(5)
           GPIO.output(LED1,GPIO.LOW)
           GPIO.output(LED2,GPIO.HIGH)
           GPIO.output(LED3,GPIO.LOW)
           print("Yellow trafic light")
           time.sleep(1)
           GPIO.output(LED2,GPIO.LOW)
           GPIO.output(LED3,GPIO.HIGH)  
           GPIO.output(LED1,GPIO.LOW)
           print("Red trafic light")
           time.sleep(4)
           
            
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
