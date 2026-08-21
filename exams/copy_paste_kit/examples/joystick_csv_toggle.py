import os
import time

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO

from exams.copy_paste_kit.adc_reader import ADCReader
from exams.copy_paste_kit.button_toggle import ButtonToggle
from exams.copy_paste_kit.csv_logger import CSVLogger
from exams.copy_paste_kit.joystick import Joystick


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    adc = ADCReader()
    joystick = Joystick(adc, x_channel=6, y_channel=5)
    toggle = ButtonToggle(pin=7, initial=True, name="Logging")
    logger = CSVLogger("joystick_log.csv", ["timestamp", "x", "y", "direction"])

    print("Press joystick button to toggle CSV logging.")

    try:
        while True:
            direction, x_value, y_value = joystick.direction()

            if toggle.is_on():
                logger.write(x_value, y_value, direction)

            print(f"X: {x_value:3d}  Y: {y_value:3d}  Direction: {direction:6s}  Log: {toggle.is_on()}")
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        logger.close()
        adc.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
