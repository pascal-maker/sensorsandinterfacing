import time
import RPi.GPIO as GPIO

from shift_register import ShiftRegister
from led_matrix import LedMatrix8x8


BTN_UP = 5
BTN_DOWN = 6
BTN_LEFT = 13
BTN_RIGHT = 19
JOY_CLICK = 7


def setup_buttons():
    buttons = [BTN_UP, BTN_DOWN, BTN_LEFT, BTN_RIGHT, JOY_CLICK]

    for button in buttons:
        GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def button_pressed(pin):
    return GPIO.input(pin) == GPIO.LOW


try:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    setup_buttons()

    shift_reg = ShiftRegister()
    matrix = LedMatrix8x8(shift_reg)

    cursor_x = 0
    cursor_y = 0

    cursor_visible = True
    last_blink_time = time.time()

    last_move_time = 0
    last_click_time = 0

    while True:
        now = time.time()

        # blink cursor
        if now - last_blink_time > 0.3:
            cursor_visible = not cursor_visible
            last_blink_time = now

        # move cursor
        if now - last_move_time > 0.2:
            if button_pressed(BTN_UP):
                cursor_y = max(0, cursor_y - 1)
                last_move_time = now
                print(f"UP pressed - Pos: ({cursor_x}, {cursor_y})")

            elif button_pressed(BTN_DOWN):
                cursor_y = min(7, cursor_y + 1)
                last_move_time = now
                print(f"DOWN pressed - Pos: ({cursor_x}, {cursor_y})")

            elif button_pressed(BTN_LEFT):
                cursor_x = max(0, cursor_x - 1)
                last_move_time = now
                print(f"LEFT pressed - Pos: ({cursor_x}, {cursor_y})")

            elif button_pressed(BTN_RIGHT):
                cursor_x = min(7, cursor_x + 1)
                last_move_time = now
                print(f"RIGHT pressed - Pos: ({cursor_x}, {cursor_y})")

        # joystick click = draw/remove dot
        if button_pressed(JOY_CLICK) and now - last_click_time > 0.3:
            print("CLICK pressed (Toggle Dot)")
            matrix.toggle_pixel(cursor_x, cursor_y)
            last_click_time = now

        matrix.refresh_once(cursor_x, cursor_y, cursor_visible)

except KeyboardInterrupt:
    GPIO.cleanup()