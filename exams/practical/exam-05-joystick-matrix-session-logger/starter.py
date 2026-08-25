"""Practice Exam 5 starter — complete the TODO sections yourself."""

import os
import time

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO

from exams.copy_paste_kit.adc_reader import ADCReader
from exams.copy_paste_kit.button_toggle import ButtonToggle
from exams.copy_paste_kit.csv_logger import CSVLogger
from exams.copy_paste_kit.joystick import Joystick
from exams.copy_paste_kit.led_matrix_8x8 import LedMatrix8x8
from exams.copy_paste_kit.shift_register import ShiftRegister


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    adc = ADCReader()
    joystick = Joystick(adc, x_channel=6, y_channel=5)
    session = ButtonToggle(pin=20, initial=False, name="Logging")
    logger = CSVLogger(
        "session.csv",
        ["event", "x", "y", "pixel_state", "joystick_x", "joystick_y"],
    )
    matrix = LedMatrix8x8(ShiftRegister())
    matrix.start()

    x = 3
    y = 3
    previous_direction = "CENTER"

    try:
        while True:
            direction, raw_x, raw_y = joystick.direction()

            # TODO: move once only after CENTER, clamp x/y, and update matrix.
            # TODO: debounce GPIO 7 and toggle the selected saved pixel.
            # TODO: log accepted actions only while session.is_on() is True.
            previous_direction = direction
            time.sleep(0.02)
    except KeyboardInterrupt:
        print("Practice stopped")
    finally:
        matrix.cleanup()
        logger.close()
        adc.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
