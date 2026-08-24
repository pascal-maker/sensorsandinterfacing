"""Identify the byte order and bit order used by an 8x8 LED matrix."""

import time

import RPi.GPIO as GPIO

from shift_register import ShiftRegister


# Each tuple contains: label, byte packing, shift direction, reverse columns.
MODES = (
    ("A", "ROW_COLUMN", ShiftRegister.MSB_TO_LSB, False),
    ("B", "ROW_COLUMN", ShiftRegister.MSB_TO_LSB, True),
    ("C", "COLUMN_ROW", ShiftRegister.MSB_TO_LSB, False),
    ("D", "COLUMN_ROW", ShiftRegister.MSB_TO_LSB, True),
    ("E", "ROW_COLUMN", ShiftRegister.LSB_TO_MSB, False),
    ("F", "ROW_COLUMN", ShiftRegister.LSB_TO_MSB, True),
    ("G", "COLUMN_ROW", ShiftRegister.LSB_TO_MSB, False),
    ("H", "COLUMN_ROW", ShiftRegister.LSB_TO_MSB, True),
)


def pixel_value(x, y, packing, reverse_column):
    """Build one active-high row and one active-low column selector."""
    row_byte = 1 << y
    column_position = 7 - x if reverse_column else x
    column_byte = ~(1 << column_position) & 0xFF

    if packing == "ROW_COLUMN":
        return (row_byte << 8) | column_byte
    return (column_byte << 8) | row_byte


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    shift_register = ShiftRegister()

    print("Matrix wiring test started. Press Ctrl+C to stop.")
    print("Find the mode with BOTH correct vertical and horizontal movement.")

    try:
        while True:
            for label, packing, direction, reverse_column in MODES:
                print(
                    f"MODE {label}: packing={packing}, "
                    f"direction={direction}, reverse_column={reverse_column}"
                )

                # Change only Y first. The dot should move vertically while its
                # horizontal position stays fixed.
                print(f"MODE {label} VERTICAL: X stays 0; Y moves 0 to 7")
                for _ in range(2):
                    for y in range(8):
                        value = pixel_value(
                            0,
                            y,
                            packing,
                            reverse_column,
                        )
                        shift_register.shift_out_16bit(value, direction=direction)
                        time.sleep(0.25)

                # Change only X next. The dot should move horizontally while
                # its vertical position stays fixed.
                print(f"MODE {label} HORIZONTAL: Y stays 7; X moves 0 to 7")
                for _ in range(2):
                    for x in range(8):
                        value = pixel_value(
                            x,
                            7,
                            packing,
                            reverse_column,
                        )
                        shift_register.shift_out_16bit(value, direction=direction)
                        time.sleep(0.25)

                # Blank between modes so their patterns do not blend together.
                shift_register.shift_out_16bit(0x00FF, direction=direction)
                time.sleep(0.75)
    except KeyboardInterrupt:
        print("\nMatrix wiring test stopped")
    finally:
        # Try both common blank arrangements before releasing GPIO.
        shift_register.shift_out_16bit(
            0x00FF,
            direction=ShiftRegister.MSB_TO_LSB,
        )
        shift_register.shift_out_16bit(
            0xFF00,
            direction=ShiftRegister.MSB_TO_LSB,
        )
        GPIO.cleanup()


if __name__ == "__main__":
    main()
