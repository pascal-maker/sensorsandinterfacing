from RPi import GPIO
import time


# The order of this list is important. The first pin is bit 0 (value 1),
# followed by bit 1 (value 2), bit 2 (value 4), and bit 3 (value 8).
BCD_PINS = [16, 20, 21, 26]

# Wait 0.1 seconds between measurements so the console remains readable.
POLL_INTERVAL = 0.1

# Use Broadcom (BCM) GPIO pin numbers, matching the numbers above.
GPIO.setmode(GPIO.BCM)

# Configure all four BCD pins as inputs with their internal pull-ups enabled.
# A pull-up makes an undriven input read HIGH instead of floating randomly.
for pin in BCD_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    # Poll the BCD counter continuously until the user presses Ctrl+C.
    while True:
        # Start with an empty four-bit value: 0000.
        nibble = 0

        # enumerate() supplies both the bit position (0-3) and GPIO pin.
        for bit_position, pin in enumerate(BCD_PINS):
            # GPIO.input() returns GPIO.LOW (0) or GPIO.HIGH (1).
            raw_bit = GPIO.input(pin)

            # XOR with 1 inverts one bit: 0 becomes 1 and 1 becomes 0.
            # The assignment requires inversion because the inputs are active-low.
            inverted_bit = raw_bit ^ 1

            # Display each input separately to help verify the circuit.
            print(
                f"Bit {bit_position} (GPIO {pin}): "
                f"raw={raw_bit}, inverted={inverted_bit}"
            )

            # Move the bit to its binary position with <<, then combine it
            # with the existing nibble using bitwise OR (|).
            # Example for bit 2: 1 << 2 gives 0100.
            nibble |= inverted_bit << bit_position

        # :04b formats the number as exactly four binary digits.
        print(f"BCD nibble: {nibble:04b}")

        # One BCD nibble can represent only decimal digits 0 through 9.
        # Binary values 1010 through 1111 are not valid BCD digits.
        if nibble <= 9:
            print(f"Decimal value: {nibble}")
        else:
            print(f"Invalid BCD value: {nibble}")

        # Print a blank line between measurements and pause before polling again.
        print()
        time.sleep(POLL_INTERVAL)

except KeyboardInterrupt:
    # Ctrl+C stops the infinite loop without displaying an error traceback.
    print("\nProgram stopped.")

finally:
    # Always release the GPIO pins, even if an unexpected error occurs.
    GPIO.cleanup()
