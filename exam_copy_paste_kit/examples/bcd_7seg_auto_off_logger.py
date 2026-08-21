import os
import sys
import time

os.environ.setdefault("RPI_LGPIO_CHIP", "0")
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import RPi.GPIO as GPIO

from adc_reader import ADCReader, Potentiometer
from auto_off_timer import AutoOffTimer
from bcd_input import BCDInput
from button_toggle import ButtonToggle
from csv_logger import CSVLogger
from seven_segment_display import SevenSegmentDisplay
from shift_register import ShiftRegister


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    bcd = BCDInput(pins=(16, 20, 21, 26), active_low=True)
    adc = ADCReader()
    pot = Potentiometer(adc, channel=4)
    timer = AutoOffTimer()

    shift = ShiftRegister(data_pin=22, latch_pin=27, clock_pin=17)
    display = SevenSegmentDisplay(shift, digits=4)
    toggle = ButtonToggle(pin=7, initial=False, name="Display")
    logger = CSVLogger("bcd_values.csv", ["timestamp", "bcd_value", "display_on", "auto_off"])

    last_bcd_value = bcd.read_value()
    last_log_time = 0
    display.start()

    print("BCD value appears on the 4-digit display.")
    print("Changing BCD turns display on. Button toggles display. Pot sets auto-off.")

    try:
        while True:
            raw_pot = pot.read()
            timer.update_from_raw(raw_pot)

            bcd_value = bcd.read_value()
            if bcd_value != last_bcd_value:
                last_bcd_value = bcd_value
                toggle.enabled = True
                timer.start()

            if toggle.is_on() and timer.expired():
                toggle.enabled = False
                timer.cancel()
                print("Display auto-off")

            if toggle.is_on():
                display.show_number(bcd_value)
            else:
                display.show_text("    ")

            now = time.time()
            if toggle.is_on() and now - last_log_time >= 1:
                logger.write(bcd_value, int(toggle.is_on()), timer.label())
                last_log_time = now

            print(f"BCD: {bcd_value:2d}  Display: {toggle.is_on()}  Auto-off: {timer.label()}")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopped")
    finally:
        display.cleanup()
        logger.close()
        adc.close()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
