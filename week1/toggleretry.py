import time 
from RPi import GPIO
GPIO.setmode(GPIO.BCM)
previous_state  = 0

btn = 20
led = 17

GPIO.setup(btn,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(led,GPIO.OUT)

try:
    while True:
        
        value = GPIO.input(btn)
        GPIO.output(led,not value)
        print('The value of pin {0} is {1}'.format(btn,value))
        
        time.sleep(0.5)
        
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()        
