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
    shift = ShiftRegister(data_pin=22, latch_pin=27, clock_pin=17)
    matrix = LedMatrix8x8(shift)
    toggle = ButtonToggle(pin=7, initial=True, name="Matrix graph")
    logger = CSVLogger("joystick_graph_log.csv", ["timestamp", "x", "y", "led_count"])

    matrix.start()
    print("Matrix draws scrolling graph from joystick X. Press joystick button to toggle.")

    try:
        while True:
            x_value, y_value = joystick.read()
            matrix.set_enabled(toggle.is_on())

            if toggle.is_on():
                led_count = matrix.push_graph_value(x_value)
            else:
                led_count = 0

            logger.write(x_value, y_value, led_count)
            print(f"X: {x_value:3d}  Y: {y_value:3d}  Graph LEDs: {led_count}  Matrix: {toggle.is_on()}")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        matrix.cleanup()
        logger.close()
        adc.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
