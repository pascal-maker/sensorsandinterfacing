import time
import RPi.GPIO as GPIO#importing the GPIO library

import smbus#importing the smbus library
GPIO.setmode(GPIO.BCM)#setting the mode to BCM
GPIO.setwarnings(False)#setting the warnings to false

BUTTON = 16#setting the button pin
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the button pin as input
ADC_ADDRESS = 0x48#setting the adc address
POT_CHANNEL = 0#setting the pot channel
bus = smbus.SMBus(1)#setting the bus

#Motor modes

OFF = 0#setting the mode to off
LEFT = 1#setting the mode to left
RIGHT = 2#setting the mode to right

mode = OFF#setting the mode to off
last_button_state = 1#setting the last button state to 1

def read_adc(channel):#reading the adc value
    control_byte = 0x40 | channel#setting the control byte
    bus.write_byte(ADC_ADDRESS, control_byte)#writing the control byte to the bus
    value = bus.read_byte(ADC_ADDRESS)#reading the adc value
    return value
    
try:
    current_button_state = GPIO.input(BUTTON)#reading the button state
    #detect new button press
    if current_button_state == 0 and last_button_state == 1:#detecting new button press
        mode = (mode + 1) % 3#changing the mode
        time.sleep(0.2)#waiting for 0.2 seconds
    last_button_state = current_button_state#setting the last button state to current button state
    
    adc_value = read_adc(POT_CHANNEL)#reading the adc value
    speed = adc_value / 2.55 * 100.0#calculating the speed

    if mode == OFF:#checking the mode
        print(f"Mode: OFF| ADC: {adc_value:3} | Speed: {speed:5.1f}%")#printing the mode and speed
    elif mode == LEFT:#checking the mode
        print(f"Mode: LEFT| ADC: {adc_value:3} | Speed: {speed:5.1f}%")#printing the mode and speed
    elif mode == RIGHT:
        print(f"Mode: RIGHT| ADC: {adc_value:3} | Speed: {speed:5.1f}%")
    time.sleep(0.1)
except KeyboardInterrupt:
    GPIO.cleanup()
    print("Motor stopped by user")
    