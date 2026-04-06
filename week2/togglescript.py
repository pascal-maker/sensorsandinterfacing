from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)#set the mode to BCM
button = 20#define the button pin
led_pin = 17#define the led pin
GPIO.setup(button,GPIO.IN,pull_up_down=GPIO.PUD_UP)#set the button pin as input with pull up
GPIO.setup(led_pin,GPIO.OUT)#set the led pin as output
n_presses = 0#initialize the number of presses
led_state = 0#initialize the led state

GPIO.output(led_pin, led_state)

try:
    previous_state = GPIO.input(button)#initialize the previous state
    while True:
        current_state = GPIO.input(button)#get the current state
        if current_state != previous_state:#check if the button state has changed
            if current_state == GPIO.LOW: #check if the button is pressed
                led_state = not led_state #toggle the led state
                GPIO.output(led_pin, led_state)#output the led state
                print('Button is pressed, led is now {}'.format(led_state))#print the led state
                
                n_presses += 1 #increment the number of presses
                print('Number of presses: {}'.format(n_presses))#print the number of presses
                time.sleep(0.05)#wait for 0.5 seconds
            else:
                print('Button is released')#print the button state
            previous_state = current_state
        time.sleep(0.01)        

except KeyboardInterrupt:#when the user press ctrl+c
    print("Exiting the program")
finally:    
    GPIO.cleanup()#cleanup the GPIO pins
    