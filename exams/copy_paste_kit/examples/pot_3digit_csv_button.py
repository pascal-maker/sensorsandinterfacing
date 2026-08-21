import os
import time

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO

from exams.copy_paste_kit.adc_reader import ADCReader, Potentiometer
from exams.copy_paste_kit.button_toggle import ButtonToggle
from exams.copy_paste_kit.csv_logger import CSVLogger
from exams.copy_paste_kit.seven_segment_display import SevenSegmentDisplay
from exams.copy_paste_kit.shift_register import ShiftRegister


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    adc = ADCReader()
    pot = Potentiometer(adc, channel=2)
    shift = ShiftRegister(data_pin=22, latch_pin=27, clock_pin=17)
    display = SevenSegmentDisplay(shift, digits=3)
    toggle = ButtonToggle(pin=20, initial=True, name="Display and logging")
    logger = CSVLogger("pot_3digit_log.csv", ["timestamp", "pot_value"])

    display.start()
    print("Pot value is shown as 000-255. Press button to toggle display/logging.")

    try:
        while True:
            value = pot.read()

            if toggle.is_on():
                display.show_number(value)
                logger.write(value)
            else:
                display.show_text("   ")

            print(f"Pot: {value:3d}  Enabled: {toggle.is_on()}")
            time.sleep(0.25)

    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        display.cleanup()
        logger.close()
        adc.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
