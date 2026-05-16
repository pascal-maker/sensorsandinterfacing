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

    # cursor position on the 8x8 grid — (0,0) is top-left
    cursor_x = 0#the cursor x position
    cursor_y = 0#the cursor y position

    cursor_visible = True        # controls whether the cursor LED is on right now (toggled for blinking)
    last_blink = time.time()     # timestamp of the last blink flip
    last_move = 0                # timestamp of the last cursor move (used for debouncing)

    last_joy_state = GPIO.HIGH   # previous joystick click state — used to detect a falling edge (press event)

    try:
        while True:
            now = time.time()

            # --- Cursor blinking ---
            # Every BLINK_PERIOD seconds, flip cursor_visible so the cursor flashes on and off
            if now - last_blink > BLINK_PERIOD:#checks if the blink period has passed
                cursor_visible = not cursor_visible#flips the cursor visibility
                last_blink = now#updates the last blink time

            # --- Button movement with debounce ---
            # MOVE_DEBOUNCE prevents the cursor from flying across the grid when a button is held;
            # only one move is registered per debounce window
            if now - last_move > MOVE_DEBOUNCE:#checks if the move debounce has passed
                moved = False#sets moved to false

                if pressed(BTN_UP):#checks if the up button is pressed
                    cursor_y = max(0, cursor_y - 1)  # clamp to top edge prevents going to high values we have 8 rows  -1 means top left value 0 is bottom left so when we minus 1 it goes to high values
                    moved = True#sets moved to true

                elif pressed(BTN_DOWN):#checks if the down button is pressed
                    cursor_y = min(7, cursor_y + 1)  # clamp to bottom edge prevents going to low values we have 8 rows  -1 means top left value 0 is bottom left so when we add 1 it goes to low values
                    moved = True#sets moved to true

                elif pressed(BTN_LEFT):#checks if the left button is pressed
                    cursor_x = max(0, cursor_x - 1)  # clamp to left edge
                    moved = True#sets moved to true

                elif pressed(BTN_RIGHT):#checks if the right button is pressed
                    cursor_x = min(7, cursor_x + 1)  # clamp to right edge prevents going to low values we have 8 rows  -1 means top left value 0 is bottom left so when we add 1 it goes to low values
                    moved = True#sets moved to true

                if moved:#checks if the cursor was moved
                    last_move = now#updates the last move time
                    cursor_visible = True#makes the cursor visible
                    last_blink = now#updates the last blink time
                    print("Move ->", (cursor_x, cursor_y))#prints the cursor position

            # --- Joystick click — toggle pixel (falling-edge detection) ---
            joy_state = GPIO.input(JOY_CLICK)#gets the joystick state

            # HIGH→LOW transition means the button was just pressed (not held)
            if last_joy_state == GPIO.HIGH and joy_state == GPIO.LOW:#checks if the joystick was just pressed
                matrix.toggle_pixel(cursor_x, cursor_y)  # permanently flip the LED at the cursor

                state = "ON" if matrix.get_pixel(cursor_x, cursor_y) else "OFF"#gets the state of the pixel
                cursor_visible = True   # make cursor visible so you see where you just toggled
                last_blink = now#updates the last blink time

                print(f"Toggled pixel {(cursor_x, cursor_y)} to {state}")#prints the pixel state

            last_joy_state = joy_state#stores the joystick state for the next iteration's edge detection

            # --- Refresh display ---
            # Redraws the full matrix every loop, overlaying the blinking cursor at (cursor_x, cursor_y)
            matrix.refresh_once(cursor_x, cursor_y, cursor_visible)#refreshes the led matrix once

    except KeyboardInterrupt:#catches the keyboard interrupt
        # Ctrl+C raises KeyboardInterrupt; catch it here for a clean exit instead of a traceback
        print("Exiting...")#prints that the program is exiting

    finally:
        try:
            matrix.blank()#we blank the matrix
        except Exception:
            pass

        GPIO.cleanup()#we clean up the GPIO
        print("GPIO cleaned up")#we print that the GPIO has been cleaned up

if __name__ == "__main__":#this is the main function
    main()#we run the main function