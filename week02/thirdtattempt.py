from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)

green = 9
yellow = 10

red = 11

GPIO.setup(green,GPIO.OUT)
GPIO.setup(yellow,GPIO.OUT)
GPIO.setup(red,GPIO.OUT)


def set_lights(g,y,r):
    GPIO.output(green,g)
    GPIO.output(yellow,y)
    GPIO.output(red,r)
    


try:
    while True:
        set_lights(GPIO.HIGH,GPIO.LOW,GPIO.LOW)
        print("Green")
        time.sleep(5)
        
        
        set_lights(GPIO.LOW,GPIO.HIGH,GPIO.LOW)
        print("Yellow")
        time.sleep(1)
        
        
        set_lights(GPIO.LOW,GPIO.LOW,GPIO.HIGH)
        print("Red")
        time.sleep(4)
    
except KeyboardInterrupt:
    print("Program Stoppped")
    
finally:
    GPIO.cleanup()    
        
        
        
        



