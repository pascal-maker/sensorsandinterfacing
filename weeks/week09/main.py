import RPi.GPIO as GPIO #imports the RPi.GPIO module
GPIO.setmode(GPIO.BCM) # sets the pin numbering mode to BCM
import time#imports the time module
from led_matrix import LedMatrix8x8#imports the LEDMatrix8x8 class
from fourdigit7segmentclass import FourDigit7Segment#imports the FourDigit7Segment class
from displaythread import DisplayThread#imports the DisplayThread class
from shift_register import ShiftRegister#imports the ShiftRegister class
LETTER_A = [
    0b00111100,#this is the pattern for the letter 
    0b01000010,#this is the pattern for the letter 
    0b01000010,#this is the pattern for the letter
    0b01111110,#this is the pattern for the letter 
    0b01000010,#this is the pattern for the letter 
    0b01000010,#this is the pattern for the letter 
    0b01000010,#this is the pattern for the letter 
    0b00000000,#this is the pattern for the letter 
]

try:
    shiftregister = ShiftRegister()#initializes the shift register
    display= FourDigit7Segment(shiftregister,common_anode=True)#initializes the four digit 7 segment display
    display.putFilledValue("12",fill_char="0",align="right")#puts the value on the display
    display_thread = DisplayThread(display)#creates the display thread
    display_thread.start()    
    time.sleep(2)#waits for 2 seconds
    display_thread.put("ABCD")#puts the value on the display
    time.sleep(2)#waits for 2 seconds

    display_thread.put("1")#puts the value on the display
    time.sleep(2)#waits for 2 seconds


    matrix = LedMatrix8x8(shiftregister)#creates the led matrix
    matrix.row_data = list(LETTER_A)#sets the pattern of the led matrix
    while True:
        matrix.refresh_once()
except KeyboardInterrupt:
    GPIO.cleanup()
    
    
    