import os
import time

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO

from exams.copy_paste_kit.adc_reader import ADCReader, Potentiometer
from exams.copy_paste_kit.button_toggle import ButtonToggle
from exams.copy_paste_kit.csv_logger import CSVLogger
from exams.copy_paste_kit.led_bar_graph import LedBarGraph
from exams.copy_paste_kit.shift_register import ShiftRegister


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    adc = ADCReader()
    pot = Potentiometer(adc, channel=2)
    shift = ShiftRegister(data_pin=22, latch_pin=27, clock_pin=17)
    bar = LedBarGraph(shift, led_count=10)
    toggle = ButtonToggle(pin=20, initial=True, name="Bar graph")
    logger = CSVLogger("pot_bargraph_log.csv", ["timestamp", "pot_value", "led_count"])

    try:
        while True:
            value = pot.read()

            if toggle.is_on():
                led_count = bar.show_value(value)
            else:
                led_count = 0
                bar.clear()

            logger.write(value, led_count)
            print(f"Pot: {value:3d}  LEDs: {led_count:2d}  Bar: {toggle.is_on()}")
            time.sleep(0.25)

    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        bar.clear()
        logger.close()
        adc.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
