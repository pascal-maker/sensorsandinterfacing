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

display_thread = None
matrix = None

try:
    shiftregister = ShiftRegister()#initializes the shift register
    display = FourDigit7Segment(shiftregister, common_anode=True)

    # 1. Display a single value on a single digit.
    print("Test 1: showing 1 on digit 1")
    display.show_one_digit(0, "1")
    time.sleep(2)

    # 2. Put the same value on all four digits through fast multiplexing.
    print("Test 2: showing 2 on every digit")
    display.putValue("2222")
    end_time = time.time() + 2
    while time.time() < end_time:
        display.refresh_once()

    # 3. Show the value on each physical digit separately at a visible speed.
    print("Test 3: showing 3 on each digit, one at a time")
    for digit_index in range(4):
        display.show_one_digit(digit_index, "3")
        time.sleep(0.5)

    # 4/5. A thread refreshes unique hexadecimal characters continuously,
    # while a Queue passes new string values from this main thread.
    print("Test 4: threaded display and Queue; showing 1A2F")
    display_thread = DisplayThread(display)
    display_thread.start()
    display_thread.put("1A2F")
    time.sleep(2)
    display_thread.put("ABCD")
    time.sleep(2)
    display.setCounter(9)
    display.increment()
    time.sleep(2)

    # Stop the display thread before the matrix shares the shift register.
    display_thread.stop()
    display_thread = None

    print("LED matrix test: displaying the letter A (Ctrl+C to stop)")
    matrix = LedMatrix8x8(shiftregister)#creates the led matrix
    matrix.row_data = list(LETTER_A)#sets the pattern of the led matrix
    while True:
        matrix.refresh_once()
except KeyboardInterrupt:
    print("\nWeek 09 demonstration stopped")
finally:
    if display_thread is not None:
        display_thread.stop()
    if matrix is not None:
        matrix.blank()
    GPIO.cleanup()
    
