from RPi import GPIO
import time

pedestrian_requsted = False

GPIO.setmode(GPIO.BCM)
ped_btn = 20
green = 9
yellow = 10

red = 11
GPIO.setup(ped_btn,GPIO.IN,pull_up_down=GPIO.PUD_UP)
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
        
        start = time.time()
        while time.time() - start < 5:
            
         if GPIO.input(ped_btn) == GPIO.LOW:
            pedestrian_requsted = True
            print("pedestrian button pressed")
         time.sleep(0.55)
        
        
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
        
        
        
        



