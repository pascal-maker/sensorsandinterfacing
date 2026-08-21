import os
import time

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO

from exams.copy_paste_kit.adc_reader import ADCReader, Potentiometer
from exams.copy_paste_kit.csv_logger import CSVLogger


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    adc = ADCReader()
    pot = Potentiometer(adc, channel=2)
    logger = CSVLogger("potentiometer_log.csv", ["timestamp", "pot_value", "percent"])

    try:
        while True:
            value = pot.read()
            percent = round((value / 255) * 100)
            logger.write(value, percent)
            print(f"Pot: {value:3d}  Percent: {percent:3d}%")
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        logger.close()
        adc.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
