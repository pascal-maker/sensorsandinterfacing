import RPi.GPIO as GPIO
import time
button_pin = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)#pullup
previous_state = GPIO.input(button_pin)

while True:
    current_state = GPIO.input(button_pin)
    if current_state != previous_state:
        if current_state == GPIO.LOW:#button pressed
            print("Button was pressed")
        else:
            print("Button was released")#button released
        previous_state = current_state
    time.sleep(0.01)#debounce small delay

