import time#
from RPi import GPIO#import the RPi.GPIO library 

LED1 = 9#define the led pins
LED2 = 10#
LED3 = 11#
BTN1 = 20#
BTN2 = 21#
LEDS = [LED1, LED2, LED3]#store led pins in a list

GPIO.setmode(GPIO.BCM)#set the GPIO mode
for led in LEDS:#setting up the leds
    GPIO.setup(led, GPIO.OUT)#the leds are outputs tell the pi this pin is an output
    GPIO.output(led, GPIO.LOW)#start with led off  each interaction handles one led - first configuring the pin direction,then setting its inital actual state

GPIO.setup(BTN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)#set up the button as an input with pull-up resistor
GPIO.setup(BTN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)#set up the button as an input with pull-up resistor

mode = 0#initialize the mode which tracks which mode the program is in. start at 0 meaning  no led LED is on. mode 1 2 and 3 correspond to led1 2 and 3 being on
previous_btn1_state = GPIO.input(BTN1)#initialize the previous state of the button

def all_off():#function to turn off all leds
    print("Turning all LEDs off")
    for led in LEDS:#loop through all the leds
        GPIO.output(led, GPIO.LOW)#turn off the leds

def show_mode():#function to show the current mode
    print(f"Showing mode: {mode}")
    all_off()# calls all off to clear everything then light extactly one led based on the current mode value. you need to turn off leds before setting state because you need to know the previous state
    if mode == 1:#if mode is 1 turn on led1
        GPIO.output(LED1,GPIO.HIGH)
    elif mode == 2:#if mode is 2 turn on led2
        GPIO.output(LED2,GPIO.HIGH)
    elif mode == 3:#if mode is 3 turn on led3
        GPIO.output(LED3,GPIO.HIGH)

try:
    while True:
        current_btn1 = GPIO.input(BTN1)#get the current state of button 1
        btn2_state  = GPIO.input(BTN2)#get the current state of button 2

        if btn2_state == GPIO.LOW:#if button 2 is pressed while btn2 is held down all leds toggle o/off every 0.3 seconds creating a flashing effect. 0.3 is debouncing effect here 
            print("Button 2 is pressed! Flashing LEDs...")
            for led in LEDS:#loop through all the leds
                GPIO.output(led,not GPIO.input(led))#toggle the leds
            time.sleep(0.3) #debounce for button 2


            if GPIO.input(BTN2) == GPIO.HIGH:#if button 2 is released   when btn2 is released , all leds turn off cleany so you dont end up with led stuck on.
                all_off()#turn off all the leds
        else:
            if previous_btn1_state == GPIO.HIGH and current_btn1 == GPIO.LOW: # detect a falling edge when the signal goes from high-> low extact moment the button is pressed you can only react to extact transitions same falling edge eecruiona s before only react at the extact moment of press.
                time.sleep(0.05)#debounce#waiting 0.05s for the signal to get stable

                if GPIO.input(BTN1) == GPIO.LOW:#if button 1 is pressed
                    print("Button 1 is pressed! Incrementing mode...")
                    mode = mode + 1 #cycles through modes when it exceeds 3 it resets back to 0 all off. this is called module cycling.

                    if mode > 3:#if mode is greater than 3 reset it to 0    
                        mode = 0#0 is for off mode

                    show_mode()#show the current mode updates the leds to reflect new mode value. 
                

            previous_btn1_state = current_btn1#update the previous state of the button this is what makes edge detection work on the next loop interation.
            time.sleep(0.01)#waiting  0.01s for the signal to get stable

except KeyboardInterrupt:
    print("Program Stopped")#if keyboard interrupt is received print stopped message
finally:
    all_off()  # ensure all leds are off when program exits
    GPIO.cleanup() # release the GPIO pins
            
###############################################################
### What the code does and the logic behind it              ###
###                                                         ###
### First we define the LED pins — as in the exercise,      ###
### three LEDs are required and two buttons. We then loop   ###
### through the LEDs, set them as outputs and disable       ###
### them. We do the setup and we start with mode 0 so the   ###
### program knows its starting state — modes 1, 2 and 3     ###
### correspond to each LED being on. We then create         ###
### another variable called previous_btn1_state to          ###
### initialize the previous state of button 1.              ###
###                                                         ###
### We define all_off() which turns off all the LEDs by     ###
### looping through our list of LEDs and setting them to    ###
### LOW. We then define show_mode() to show the current     ###
### mode — we first call all_off() to clear everything,     ###
### then we say if mode is 1 turn on LED1, if mode is 2     ###
### turn on LED2, if mode is 3 turn on LED3.                ###
###                                                         ###
### We then use a try block. We read the current button     ###
### states first. We check if button 2 is pressed — if so   ###
### we loop through all the LEDs and toggle them using      ###
### not GPIO.input(led). If button 2 is released we turn    ###
### all LEDs off because we need to toggle them all         ###
### together so we use a list of LEDs. Otherwise, if        ###
### button 1 was previously not pressed and is now pressed  ###
### we detect a falling edge. We apply a debounce, and if   ###
### button 1 is confirmed pressed we cycle through the      ###
### modes by incrementing mode by 1. If mode exceeds 3 we   ###
### reset it to 0 and call show_mode() to update the LEDs.  ###
### Finally we update previous_btn1_state with the          ###
### current button state.                                   ###
###############################################################