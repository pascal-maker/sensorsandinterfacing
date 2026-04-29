" transform the  example  int oa toggle system. use the button connected to GPIO20 as a toggle switch for the led on GPIO 17 toggling means 1 press: turn on ; stay on until te next press: turn off stay off until next press;"
from RPi import GPIO#importing the Rpi.GPIO library
import time # importing time library
btn = 20 # we define btn as 20
led = 17 # we define led as 17
GPIO.setmode(GPIO.BCM)#define pinnaming method

GPIO.setup(btn,GPIO.IN,pull_up_down=GPIO.PUD_UP)#setting up the button as input with pull up resistor
GPIO.setup(led,GPIO.OUT)#setting up the led as output
led_on = False# we define led_on as false
previous_btn_state = GPIO.HIGH# we define previous_btn_state as HIGH

try:
    while True:
        current_btn_state = GPIO.input(btn)# reading the button state
        if previous_btn_state == GPIO.HIGH and current_btn_state == GPIO.LOW:#check if button was released and is now pressed
            led_on = not led_on#toggle led
            GPIO.output(led,led_on)#output led 
           
           if led_on:# check if led is on
            print("led is on")#printing
           else:
            print("led is off")#printing
           time.sleep(0.2) # a debounce 
           previous_btn_state = current_btn_state# updating the previous state with the current state
           
except KeyboardInterrupt:#ignoring the keyboard interrupt
    pass
finally:#cleaning up the GPIO pins
    GPIO.cleanup()

#INPUT (with pull-up):
#INPUT (with pull-up):#
#HIGH = not pressed#
#LOW  = pressed#

#OUTPUT:#
#HIGH = on#
#LOW  = off#
        




