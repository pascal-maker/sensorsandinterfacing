import time
import threading
import queue
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

def setup_buttons():#this function sets up the buttons
    for btn in BUTTONS:#we loop through each button
        GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)#we set the button to input and pull up to up

def main():#this is the main function
    GPIO.setmode(GPIO.BCM)#we set the mode to BCM
    GPIO.setwarnings(False)#we set the warnings to false

    setup_buttons()#we set up the buttons

    shift_reg = ShiftRegister()#we create a shift register object
    matrix = LedMatrix8x8(shift_reg)#we create a led matrix object

    print("Week 09 LED-matrix drawing program started")
    print("Use GPIO 20/21/26/16 to move and joystick GPIO 7 to draw.")
    print("Press Ctrl+C to stop.")
    print(
        "Initial inputs: "
        f"UP={GPIO.input(BTN_UP)} "
        f"DOWN={GPIO.input(BTN_DOWN)} "
        f"LEFT={GPIO.input(BTN_LEFT)} "
        f"RIGHT={GPIO.input(BTN_RIGHT)} "
        f"JOY={GPIO.input(JOY_CLICK)}"
    )

    # cursor position on the 8x8 grid — (0,0) is top-left
    cursor_x = 0#the cursor x position
    cursor_y = 0#the cursor y position

    cursor_visible = True        # controls whether the cursor LED is on right now (toggled for blinking)
    last_blink = time.monotonic()# timestamp of the last blink flip
    press_queue = queue.SimpleQueue()

    def remember_press(pin):
        press_queue.put(pin)

    for pin in BUTTONS:
        GPIO.add_event_detect(
            pin,
            GPIO.FALLING,
            callback=remember_press,
            bouncetime=150,
        )

    # Refresh the multiplexed display independently so input polling is never
    # delayed by shifting a complete eight-row frame.
    display_state = {
        "cursor_x": cursor_x,
        "cursor_y": cursor_y,
        "cursor_visible": cursor_visible,
    }
    stop_display = threading.Event()

    def refresh_display():
        while not stop_display.is_set():
            matrix.refresh_once(
                display_state["cursor_x"],
                display_state["cursor_y"],
                display_state["cursor_visible"],
            )

    display_thread = threading.Thread(target=refresh_display, daemon=True)
    display_thread.start()

    try:
        while True:
            now = time.monotonic()

            # --- Cursor blinking ---
            # Every BLINK_PERIOD seconds, flip cursor_visible so the cursor flashes on and off
            if now - last_blink > BLINK_PERIOD:#checks if the blink period has passed
                cursor_visible = not cursor_visible#flips the cursor visibility
                display_state["cursor_visible"] = cursor_visible
                last_blink = now#updates the last blink time

            try:
                pressed_pin = press_queue.get_nowait()
            except queue.Empty:
                pressed_pin = None

            old_position = (cursor_x, cursor_y)

            if pressed_pin == BTN_UP:
                cursor_y = max(0, cursor_y - 1)
            elif pressed_pin == BTN_DOWN:
                cursor_y = min(7, cursor_y + 1)
            elif pressed_pin == BTN_LEFT:
                cursor_x = max(0, cursor_x - 1)
            elif pressed_pin == BTN_RIGHT:
                cursor_x = min(7, cursor_x + 1)

            if (cursor_x, cursor_y) != old_position:
                cursor_visible = True
                display_state["cursor_x"] = cursor_x
                display_state["cursor_y"] = cursor_y
                display_state["cursor_visible"] = cursor_visible
                last_blink = now
                print("Move ->", (cursor_x, cursor_y))

            # LOW is a confirmed press. Holding the joystick button cannot
            # trigger it again until it has first been released.
            if pressed_pin == JOY_CLICK:
                matrix.toggle_pixel(cursor_x, cursor_y)
                state = "ON" if matrix.get_pixel(cursor_x, cursor_y) else "OFF"
                cursor_visible = True
                display_state["cursor_visible"] = cursor_visible
                last_blink = now
                print(f"Toggled pixel {(cursor_x, cursor_y)} to {state}")

            # Poll controls at 200 Hz while the background thread refreshes
            # the multiplexed matrix continuously.
            time.sleep(0.005)

    except KeyboardInterrupt:#catches the keyboard interrupt
        # Ctrl+C raises KeyboardInterrupt; catch it here for a clean exit instead of a traceback
        print("Exiting...")#prints that the program is exiting

    finally:
        stop_display.set()
        display_thread.join(timeout=1)
        for pin in BUTTONS:
            try:
                GPIO.remove_event_detect(pin)
            except RuntimeError:
                pass
        try:
            matrix.blank()#we blank the matrix
        except Exception:
            pass

        GPIO.cleanup()#we clean up the GPIO
        print("GPIO cleaned up")#we print that the GPIO has been cleaned up

if __name__ == "__main__":#this is the main function
    main()#we run the main function
