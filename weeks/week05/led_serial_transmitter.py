"""Transmit an ASCII message bit-by-bit using the blue LED as TX."""

import time

import RPi.GPIO as GPIO


# BCM GPIO 13 controls the blue segment of the RGB LED used in this project.
TX_PIN = 13# 
BIT_DELAY = 0.2
CHARACTER_DELAY = 1.0
MESSAGE = "hello"


def send_byte(byte):
    """Send one byte through TX_PIN, most significant bit first."""
    # A byte is an 8-bit number, so its valid decimal range is 0 to 255.
    # Stop with a clear error if the function receives an invalid value.
    if not 0 <= byte <= 255:
        raise ValueError("send_byte() requires a value between 0 and 255")

    # Visit bit positions 7, 6, 5, 4, 3, 2, 1, and 0. Starting at position 7
    # sends the most significant bit (MSB) first.
    for bit_position in range(7, -1, -1):
        # Shift the selected bit into the rightmost position. AND with 1 then
        # removes all the other bits, leaving only a 0 or 1.
        bit = (byte >> bit_position) & 1

        # Print each bit immediately on the same line, separated by spaces.
        print(bit, end=" ", flush=True)

        # Represent a 1 with a HIGH GPIO signal and a 0 with a LOW signal.
        GPIO.output(TX_PIN, GPIO.HIGH if bit else GPIO.LOW)

        # Hold the signal for 200 ms before transmitting the next bit.
        time.sleep(BIT_DELAY)

    # Start a new output line after all eight bits have been transmitted.
    print()


def main():
    # Use Broadcom (BCM) GPIO numbering. TX_PIN = 13 therefore means GPIO 13,
    # not physical pin 13 on the Raspberry Pi header.
    GPIO.setmode(GPIO.BCM)

    # Configure the blue LED pin as an output and begin with a LOW (0) signal.
    GPIO.setup(TX_PIN, GPIO.OUT, initial=GPIO.LOW)

    # The matching finally block will clean up GPIO even if an error occurs or
    # the user stops the program by pressing Ctrl+C.
    try:
        # !r prints the Python representation of the message, including quotes.
        # For example, this displays: Transmitting: 'hello'
        print(f"Transmitting: {MESSAGE!r}")

        # Process the message one character at a time. enumerate() supplies the
        # character's index (0, 1, 2, ...) as well as the character itself.
        for index, character in enumerate(MESSAGE):
            # Convert the character into its ASCII number; for example,
            # ord("h") returns 104.
            ascii_value = ord(character)

            # Display the character, its decimal ASCII value, and its binary
            # value. :08b formats the number as eight binary digits and adds
            # leading zeroes when needed, so 104 becomes 01101000.
            print(
                f"Character {character!r}: ASCII {ascii_value}, "
                f"binary {ascii_value:08b}"
            )

            # Send the eight bits of the character's ASCII value through the
            # blue LED GPIO pin.
            send_byte(ascii_value)

            # len(MESSAGE) - 1 is the index of the final character. Wait one
            # second when another character remains, but do not add an
            # unnecessary delay after the final character.
            if index < len(MESSAGE) - 1:
                time.sleep(CHARACTER_DELAY)

        print("Transmission complete.")
    except KeyboardInterrupt:
        print("\nTransmission stopped.")
    finally:
        GPIO.output(TX_PIN, GPIO.LOW)
        GPIO.cleanup()


if __name__ == "__main__":
    main()
