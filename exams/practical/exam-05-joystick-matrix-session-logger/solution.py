"""Practice Exam 5 solution: joystick matrix drawing with session logging."""

import os
import time

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO

# Reuse the small exam-kit classes instead of rewriting each hardware driver.
from exams.copy_paste_kit.adc_reader import ADCReader
from exams.copy_paste_kit.button_toggle import ButtonToggle
from exams.copy_paste_kit.csv_logger import CSVLogger
from exams.copy_paste_kit.joystick import Joystick
from exams.copy_paste_kit.led_matrix_8x8 import LedMatrix8x8
from exams.copy_paste_kit.shift_register import ShiftRegister


# Keep all wiring and timing settings together so they are easy to check or
# change without searching through the application logic.
JOYSTICK_X_CHANNEL = 6
JOYSTICK_Y_CHANNEL = 5
JOYSTICK_CLICK_PIN = 7
SESSION_BUTTON_PIN = 20
SHIFT_DATA_PIN = 22
SHIFT_LATCH_PIN = 27
SHIFT_CLOCK_PIN = 17
LOOP_DELAY = 0.02


def clamp(value, minimum=0, maximum=7):
    """Keep a matrix coordinate inside the valid 0..7 range."""
    return max(minimum, min(maximum, value))


def log_action(logger, session, event, x, y, pixel_state, raw_x, raw_y):
    """Write an accepted action only while the logging session is active."""
    if session.is_on():
        logger.write(event, x, y, int(pixel_state), raw_x, raw_y)


def main():
    """Set up the devices and run the drawing application until Ctrl+C."""
    # BCM mode refers to GPIO numbers rather than physical header-pin numbers.
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(JOYSTICK_CLICK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # The ADS7830 converts the joystick's two analog voltages to values 0..255.
    adc = ADCReader()
    joystick = Joystick(
        adc,
        x_channel=JOYSTICK_X_CHANNEL,
        y_channel=JOYSTICK_Y_CHANNEL,
    )
    # GPIO 20 uses an interrupt internally to toggle CSV logging on each press.
    session = ButtonToggle(
        pin=SESSION_BUTTON_PIN,
        initial=False,
        name="Logging",
    )
    # CSVLogger adds a timestamp before the values supplied to logger.write().
    logger = CSVLogger(
        "session.csv",
        [
            "timestamp",
            "event",
            "x",
            "y",
            "pixel_state",
            "joystick_x",
            "joystick_y",
        ],
    )
    # Two chained 74HC595 registers drive the rows and columns of the matrix.
    shift_register = ShiftRegister(
        data_pin=SHIFT_DATA_PIN,
        latch_pin=SHIFT_LATCH_PIN,
        clock_pin=SHIFT_CLOCK_PIN,
    )
    matrix = LedMatrix8x8(shift_register)

    # Each list entry stores the eight vertical pixels in one matrix column.
    saved_columns = [0x00] * 8
    # (3, 3) is one of the four centre cells of an 8x8 matrix.
    cursor_x = 3
    cursor_y = 3
    # A move is allowed only after the joystick has returned to CENTER.
    previous_direction = "CENTER"
    # Remembering the previous click level provides one action per button press.
    click_was_pressed = False

    matrix.start()
    print("Joystick matrix session logger started")
    print("Move the joystick, click to draw/erase, GPIO 20 toggles logging.")

    try:
        while True:
            # direction() returns a named direction plus both raw ADC readings.
            direction, raw_x, raw_y = joystick.direction()

            # Accept a direction only if the previous accepted state was CENTER.
            # The user must release the joystick before another move is possible.
            if direction != "CENTER" and previous_direction == "CENTER":
                old_position = (cursor_x, cursor_y)
                if direction == "LEFT":
                    cursor_x = clamp(cursor_x - 1)
                elif direction == "RIGHT":
                    cursor_x = clamp(cursor_x + 1)
                elif direction == "UP":
                    cursor_y = clamp(cursor_y - 1)
                elif direction == "DOWN":
                    cursor_y = clamp(cursor_y + 1)

                # A direction pressed against an edge is clamped and is not
                # considered an accepted move, so it is not written to CSV.
                if (cursor_x, cursor_y) != old_position:
                    pixel_state = bool(
                        saved_columns[cursor_x] & (1 << cursor_y)
                    )
                    log_action(
                        logger,
                        session,
                        "move",
                        cursor_x,
                        cursor_y,
                        pixel_state,
                        raw_x,
                        raw_y,
                    )
                    print(f"Move {direction}: ({cursor_x}, {cursor_y})")

            # A held direction remains the previous direction and cannot repeat.
            # Returning to CENTER arms the next movement.
            previous_direction = direction

            # Edge detection in the main loop gives exactly one toggle per click.
            # The internal pull-up makes a pressed joystick switch read LOW.
            click_is_pressed = GPIO.input(JOYSTICK_CLICK_PIN) == GPIO.LOW
            if click_is_pressed and not click_was_pressed:
                # XOR flips exactly one stored bit: OFF -> ON or ON -> OFF.
                saved_columns[cursor_x] ^= 1 << cursor_y
                pixel_state = bool(saved_columns[cursor_x] & (1 << cursor_y))
                log_action(
                    logger,
                    session,
                    "pixel_toggle",
                    cursor_x,
                    cursor_y,
                    pixel_state,
                    raw_x,
                    raw_y,
                )
                print(
                    f"Pixel ({cursor_x}, {cursor_y}) "
                    f"{'ON' if pixel_state else 'OFF'}"
                )
            # The next click is accepted only after this value becomes False.
            click_was_pressed = click_is_pressed

            # Overlay the cursor on a copy so it remains visible without being
            # permanently added to the saved drawing.
            visible_columns = list(saved_columns)
            visible_columns[cursor_x] |= 1 << cursor_y
            # The matrix's background thread repeatedly multiplexes this image.
            matrix.set_columns(visible_columns)
            # A short delay prevents a busy loop while remaining responsive.
            time.sleep(LOOP_DELAY)

    except KeyboardInterrupt:
        print("\nPractice Exam 5 stopped")
    finally:
        # Always stop the refresh thread before closing I2C and releasing GPIO.
        matrix.cleanup()
        logger.close()
        adc.close()
        GPIO.cleanup()
        print("Matrix blanked; CSV, I2C, and GPIO closed")


if __name__ == "__main__":
    main()
