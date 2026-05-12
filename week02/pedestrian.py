import time
from RPi import GPIO
GREEN = 9
YELLOW = 10
RED = 11


BUTTON = 20 # Pedestrian Button 

GPIO.setmode(GPIO.BCM) #Using BCM mode

GPIO.setup(GREEN,GPIO.OUT)#
GPIO.setup(YELLOW,GPIO.OUT)
GPIO.setup(RED,GPIO.OUT)
GPIO.setup(BUTTON,GPIO.IN,pull_up_down=GPIO.PUD_UP)



def all_off():# set all three leds to low off at once - a reset/clear function
    GPIO.output(GREEN,GPIO.LOW)
    GPIO.output(YELLOW,GPIO.LOW)
    GPIO.output(RED,GPIO.LOW)

def light_on_led(led):# turns on the traffic light
    all_off()#turn off green yellow and red before lighting anything
    GPIO.output(led,GPIO.HIGH)   #turns on whichever led pin was passed into the function

try:
    while True:
        #green for max 5 seconds but check button every 0.1s
        light_on_led(GREEN)  #turn on green light all three leds are turned off by the all_off function we have passed green light into the function
        print("Green light is on")# set it here because it will always print when the green light turns on, if it was in the if loop it would only print when the button was pressed so the light could change sooner for the pedestrian
        for i in range(50): #0.1 * 50 = 5 seconds loop 50 times = 5 seconds max
            if GPIO.input(BUTTON) == GPIO.LOW:#if button is pressed 
                print("Pedestrian Button Pressed")#print that button is pressed
                break
            time.sleep(0.1)# exit early dont wait the full 5s wait 0.1 between each check so 50 check per 5 seconds it polss the button every 0.1 seconds if the button is pressed it breaks out of the delay loop so the light can change sooner for the pedestrian

        light_on_led(YELLOW)#turn on yellow light
        print("Yellow light is on")
        time.sleep(1)#wait for 1 second

        light_on_led(RED)#turn on red light
        print("Red light is on")
        time.sleep(4)#wait for 4 seconds

except KeyboardInterrupt:
    print("Program Stoppped")
finally:
    GPIO.cleanup()    
