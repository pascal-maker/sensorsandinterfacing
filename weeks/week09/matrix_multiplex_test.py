"""Find the multiplex encoding that displays a complete letter A."""

import time

import RPi.GPIO as GPIO

from shift_register import ShiftRegister


LETTER_A = (
    0b00111100,
    0b01000010,
    0b01000010,
    0b01111110,
    0b01000010,
    0b01000010,
    0b01000010,
    0b00000000,
)

MODES = (
    ("A", "ROW_SCAN", "POSITIVE_NEGATIVE", ShiftRegister.MSB_TO_LSB),
    ("B", "ROW_SCAN", "NEGATIVE_POSITIVE", ShiftRegister.MSB_TO_LSB),
    ("C", "ROW_SCAN", "POSITIVE_NEGATIVE", ShiftRegister.LSB_TO_MSB),
    ("D", "ROW_SCAN", "NEGATIVE_POSITIVE", ShiftRegister.LSB_TO_MSB),
    ("E", "COLUMN_SCAN", "POSITIVE_NEGATIVE", ShiftRegister.MSB_TO_LSB),
    ("F", "COLUMN_SCAN", "NEGATIVE_POSITIVE", ShiftRegister.MSB_TO_LSB),
    ("G", "COLUMN_SCAN", "POSITIVE_NEGATIVE", ShiftRegister.LSB_TO_MSB),
    ("H", "COLUMN_SCAN", "NEGATIVE_POSITIVE", ShiftRegister.LSB_TO_MSB),
)


def pack(positive_byte, negative_byte, packing):
    """Place the active-high and active-low banks into the two registers."""
    if packing == "POSITIVE_NEGATIVE":
        return (positive_byte << 8) | negative_byte
    return (negative_byte << 8) | positive_byte


def refresh_pattern(shift_register, scan, packing, direction):
    """Refresh one complete eight-line frame."""
    if scan == "ROW_SCAN":
        for row in range(8):
            positive_byte = 1 << row
            negative_byte = ~LETTER_A[row] & 0xFF
            shift_register.shift_out_16bit(
                pack(positive_byte, negative_byte, packing),
                direction=direction,
            )
            time.sleep(0.001)
    else:
        for column in range(8):
            positive_byte = 0
            for row in range(8):
                if (LETTER_A[row] >> column) & 1:
                    positive_byte |= 1 << row
            negative_byte = ~(1 << column) & 0xFF
            shift_register.shift_out_16bit(
                pack(positive_byte, negative_byte, packing),
                direction=direction,
            )
            time.sleep(0.001)


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    shift_register = ShiftRegister()

    print("Multiplex test started. Press Ctrl+C to stop.")
    print("Each mode runs for 5 seconds. Find the mode showing a complete A.")

    try:
        while True:
            for label, scan, packing, direction in MODES:
                print(
                    f"MODE {label}: scan={scan}, packing={packing}, "
                    f"direction={direction}"
                )
                end_time = time.time() + 5
                while time.time() < end_time:
                    refresh_pattern(shift_register, scan, packing, direction)
    except KeyboardInterrupt:
        print("\nMultiplex test stopped")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
