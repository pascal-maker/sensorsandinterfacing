import os
import csv
import time
from datetime import datetime 
from RPi import GPIO

GPIO.setmode(GPIO.BCM) #set the mode of the GPIO pins to BCM
BUTTON_PINS = [20,21]#define the button pins
GPIO.setup(BUTTON_PINS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

POLL_DELAY = 0.01#delay between polls
DATA_DIR = "data"#data directory

#storage lists
timestamps = []#list to store timestamps
button_states = []#list to store button states
button_names = []#list to store button names

#keeptrack of previous states
prev_states = {}#dictionary to store previous states

#setup button pins
for pin in BUTTON_PINS:#loop through the button pins
    prev_states[pin] = GPIO.input(pin)#set the previous state of the button

#create data folder if neede
os.makedirs(DATA_DIR, exist_ok=True)#create data folder if needed
print("Program started. Press Ctrl+C to stop")
print("Tracking button state changes")



#main loop
try:
    while True:
        for pin in BUTTON_PINS:#loop through the button pins
            current_state = GPIO.input(pin)#current state of the button
            if current_state != prev_states[pin]:#if current state is different from previous state
                now = datetime.now()#current time
                timestamps.append(now)#append current time to timestamps list
                button_states.append(current_state)#append current state to button states list
                button_names.append(f"GPIO {pin}")#append button name to button names list

                if current_state == GPIO.LOW:#if button is pressed
                    print(f"{now.strftime('%Y-%m-%d %H:%M:%S.%f')} GPIO {pin} pressed")
                else:#if button is released
                    print(f"{now.strftime('%Y-%m-%d %H:%M:%S.%f')} GPIO {pin} released")
                prev_states[pin] = current_state
        time.sleep(POLL_DELAY)#wait for poll delay
except KeyboardInterrupt:#when the user press ctrl+c
    print("Exiting program")
finally:#when the program is exited
    GPIO.cleanup()#cleanup the GPIO pins