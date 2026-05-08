import RPi.GPIO as GPIO #imports the RPi.GPIO module
import time
from ledmatrixclass import LEDMatrix8x8
from fourdigit7segmentclass import FourDigit7Segment
from displaythread import DisplayThread
from shiftregister import ShiftRegister
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


    matrix = LEDMatrix8x8(shiftregister,common_anode=True)#creates the led matrix
    matrix.setPattern(LETTER_A)#sets the pattern of the led matrix
    while True:
        matrix.refresh_once()
except KeyboardInterrupt:
    GPIO.cleanup()
    
    
    