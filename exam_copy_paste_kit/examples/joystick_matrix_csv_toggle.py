import os
import sys
import time

os.environ.setdefault("RPI_LGPIO_CHIP", "0")
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import RPi.GPIO as GPIO

from adc_reader import ADCReader
from button_toggle import ButtonToggle
from csv_logger import CSVLogger
from joystick import Joystick
from led_matrix_8x8 import LedMatrix8x8
from shift_register import ShiftRegister


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    adc = ADCReader()
    joystick = Joystick(adc, x_channel=6, y_channel=5)
    shift = ShiftRegister(data_pin=22, latch_pin=27, clock_pin=17)
    matrix = LedMatrix8x8(shift)
    toggle = ButtonToggle(pin=7, initial=True, name="Matrix")
    logger = CSVLogger("joystick_matrix_log.csv", ["timestamp", "x", "y", "matrix_x", "matrix_y"])

    matrix.start()
    print("Joystick moves one LED on matrix. Press joystick button to toggle matrix.")

    try:
        while True:
            x_value, y_value = joystick.read()
            matrix_x = Joystick.value_to_index(x_value, size=8)
            matrix_y = Joystick.value_to_index(y_value, size=8)

            matrix.set_enabled(toggle.is_on())
            if toggle.is_on():
                matrix.show_cursor(matrix_x, matrix_y)

            logger.write(x_value, y_value, matrix_x, matrix_y)
            print(f"X: {x_value:3d} Y: {y_value:3d} -> LED({matrix_x}, {matrix_y}) Matrix: {toggle.is_on()}")
            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        matrix.cleanup()
        logger.close()
        adc.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
