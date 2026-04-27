import time
import RPi.GPIO as GPIO#import RPi.GPIO as GPIO so we can use its functions to control the shift register
from shift_register import ShiftRegister#we import shift_register.py so we can use its functions
from led_matrix import LedMatrix8x8#we import led_matrix.py so we can use its functions

BTN_UP = 20#this is the up button
BTN_DOWN = 21#this is the down button
BTN_LEFT = 26#this is the left button
BTN_RIGHT = 16#this is the right button
JOY_CLICK = 7#this is the click button

BUTTONS = [BTN_UP, BTN_DOWN, BTN_LEFT, BTN_RIGHT, JOY_CLICK]#we put the buttons in a list

BLINK_PERIOD = 0.3#this is the period of the blink
MOVE_DEBOUNCE = 0.18#this is the debounce time for the buttons

def setup_buttons():#this function sets up the buttons
    for btn in BUTTONS:#we loop through each button
        GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)#we set the button to input and pull up to up

def pressed(btn):#this function checks if a button is pressed
    return GPIO.input(btn) == GPIO.LOW#we return true if the button is pressed

def main():#this is the main function
    GPIO.setmode(GPIO.BCM)#we set the mode to BCM
    GPIO.setwarnings(False)#we set the warnings to false

    setup_buttons()#we set up the buttons

    shift_reg = ShiftRegister()#we create a shift register object
    matrix = LedMatrix8x8(shift_reg)#we create a led matrix object

    cursor_x = 0#this is the cursor x position
    cursor_y = 0#this is the cursor y position

    cursor_visible = True#this is the cursor visibility
    last_blink = time.time()#this is the last blink time
    last_move = 0#this is the last move time

    last_joy_state = GPIO.HIGH#this is the last joy state

    try:
        while True:
            now = time.time()#this is the current time

            if now - last_blink > BLINK_PERIOD:#if the blink period has passed
                cursor_visible = not cursor_visible#we toggle the cursor visibility
                last_blink = now#we update the last blink time

            if now - last_move > MOVE_DEBOUNCE:#if the move debounce time has passed
                moved = False#this is a flag to check if the cursor was moved

                if pressed(BTN_UP):#if the up button is pressed
                    cursor_y = max(0, cursor_y - 1)#we decrease the cursor y position
                    moved = True#we set the moved flag to true

                elif pressed(BTN_DOWN):#if the down button is pressed
                    cursor_y = min(7, cursor_y + 1)#we increase the cursor y position
                    moved = True#we set the moved flag to true

                elif pressed(BTN_LEFT):#if the left button is pressed
                    cursor_x = max(0, cursor_x - 1)#we decrease the cursor x position
                    moved = True#we set the moved flag to true

                elif pressed(BTN_RIGHT):#if the right button is pressed
                    cursor_x = min(7, cursor_x + 1)#we increase the cursor x position
                    moved = True#we set the moved flag to true

                if moved:#if the cursor was moved
                    last_move = now#we update the last move time
                    cursor_visible = True#we set the cursor visibility to true
                    last_blink = now#we update the last blink time
                    print("Move ->", (cursor_x, cursor_y))#we print the cursor position

            joy_state = GPIO.input(JOY_CLICK)#this is the joy state

            if last_joy_state == GPIO.HIGH and joy_state == GPIO.LOW:#if the last joy state is high and the joy state is low
                matrix.toggle_pixel(cursor_x, cursor_y)#we toggle the pixel at (x, y)

                state = "ON" if matrix.get_pixel(cursor_x, cursor_y) else "OFF"#
                cursor_visible = True#we set the cursor visibility to true
                last_blink = now#we update the last blink time

                print(f"Toggled pixel {(cursor_x, cursor_y)} to {state}")#we print the pixel state

            last_joy_state = joy_state#we update the last joy state

            matrix.refresh_once(cursor_x, cursor_y, cursor_visible)#we refresh the matrix once

    except KeyboardInterrupt:#if there is a keyboard interrupt
        print("Exiting...")#we print that we are exiting

    finally:
        try:
            matrix.blank()#we blank the matrix
        except Exception:
            pass

        GPIO.cleanup()#we clean up the GPIO
        print("GPIO cleaned up")#we print that the GPIO has been cleaned up

if __name__ == "__main__":#this is the main function
    main()#we run the main function