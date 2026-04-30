from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)#set the GPIO mode

green = 9#define the led pins
yellow = 10#

red = 11#define the led pins

GPIO.setup(green,GPIO.OUT)#set the leds as outputs 
GPIO.setup(yellow,GPIO.OUT)#set the leds as outputs
GPIO.setup(red,GPIO.OUT)#set the leds as outputs


def all_off():#function to turn off all the lights
    GPIO.output(green,GPIO.LOW)#turns off the green light
    GPIO.output(yellow,GPIO.LOW)#turns off the yellow light
    GPIO.output(red,GPIO.LOW)#turns off the red light
    


try:
    while True:
        all_off()#turns off all the lights
        GPIO.output(green,GPIO.HIGH)#turns on the green light
        print("Green")
        time.sleep(5)#waits for 5 seconds
        
        
        all_off()
        GPIO.output(yellow,GPIO.HIGH)#turns on the yellow light
        print("Yellow")
        time.sleep(1)#waits for 1 second
        
        
        all_off()
        GPIO.output(red,GPIO.HIGH)#turns on the red light
        print("Red")
        time.sleep(4)#waits for 4 seconds
    
except KeyboardInterrupt:
    print("Program Stoppped")#prints stopped message when keyboard interrupt is received
    
finally:
    GPIO.cleanup()    #releases the GPIO pins