from RPi import GPIO
import time


# The list order determines each input's bit position and binary weight:
#
# List position   GPIO pin   Binary weight
#       0            16        2^0 = 1
#       1            20        2^1 = 2
#       2            21        2^2 = 4
#       3            26        2^3 = 8
#
# For example, the BCD bits 0101 have weights 4 + 1, so their decimal
# value is 5. These are BCM GPIO numbers, not physical header-pin numbers.
BCD_PINS = [16, 20, 21, 26]
LED_PIN = 17

# Select BCM numbering so values such as 16 and 20 mean GPIO16 and GPIO20.
GPIO.setmode(GPIO.BCM)

# Configure all four pins as inputs by looping over the list. The internal
# pull-up holds an inactive input HIGH (1). The BCD hardware pulls an active
# input LOW (0), which is why every reading must be inverted later.
for pin in BCD_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Configure GPIO17 as an output and start HIGH so the LED begins switched on.
GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.HIGH)


def read_bcd():
    """Read, invert, position, and combine four inputs into one BCD value."""
    # Begin with an empty nibble: binary 0000.
    # This value is rebuilt from the current pin states every time read_bcd()
    # runs. It does not count or accumulate how many times a button was pressed.
    value = 0

    # enumerate() returns both the list position (0-3) and the GPIO pin.
    # The list position is also the position of that bit in the nibble.
    for bit_position, pin in enumerate(BCD_PINS):
        raw_bit = GPIO.input(pin)  # Read HIGH (1) or LOW (0).

        # XOR with 1 inverts an active-low reading:
        #     0 ^ 1 = 1
        #     1 ^ 1 = 0
        inverted_bit = raw_bit ^ 1

        # Shift the bit left into its binary position:
        #     1 << 0 = 0001 (decimal 1)
        #     1 << 1 = 0010 (decimal 2)
        #     1 << 2 = 0100 (decimal 4)
        #     1 << 3 = 1000 (decimal 8)
        # Bitwise OR (|=) combines that positioned bit with the nibble without
        # changing any bits that were already set during earlier iterations.
        # This is bit combination, not normal repeated addition. For example:
        #
        #     GPIO16 active: 0001
        #     GPIO20 active: 0010
        #                    ----
        #     combined:      0011 (decimal 3)
        #
        # Pressing GPIO16 twice does not produce 2. GPIO16 always controls only
        # bit position 0, whose fixed binary weight is 1. The final result shows
        # which BCD input bits are active at the moment they are read.
        value |= inverted_bit << bit_position

    # Return the completed nibble as a Python integer between 0 and 15.
    return value


# Read the actual hardware at startup instead of assuming the counter is zero.
initial_value = read_bcd()

# A single BCD nibble may represent only decimal digits 0 through 9.
# Values 10 through 15 (binary 1010 through 1111) are invalid BCD digits.
# This conditional expression keeps a valid reading or safely uses zero:
#
# if initial_value <= 9:          bcd_value = initial_value
# else:                           bcd_value = 0
bcd_value = initial_value if initial_value <= 9 else 0


def bcd_changed(channel):
    """Update the BCD value whenever one of the four inputs changes."""
    # The callback needs to replace the bcd_value defined outside this function.
    # Without global, Python would create a separate local variable instead.
    global bcd_value

    # An edge on one pin may change the complete four-bit number, so read all
    # four BCD pins again instead of reading only the pin named by channel.
    new_value = read_bcd()

    # A single BCD digit may contain only a value from 0 through 9.
    # Binary 1010 through 1111 means decimal 10 through 15 and is invalid BCD.
    if new_value > 9:
        # :04b displays the value as four binary digits, including leading zeros.
        print(f"Invalid BCD input: {new_value:04b} ({new_value})")
        # Keep the last valid bcd_value and stop this callback immediately.
        return

    # Store the new valid value so the main loop can use it for the LED.
    bcd_value = new_value
    print(
        # channel tells us which GPIO pin triggered this callback.
        f"GPIO {channel} changed -> "
        f"BCD: {bcd_value:04b}, decimal: {bcd_value}"
    )


def toggle_led(number_of_toggles):
    """Toggle the LED the requested number of times in one second."""
    if number_of_toggles == 0:
        # Zero means no toggles. Explicitly switch the LED on and leave it
        # unchanged for the complete one-second sequence.
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(1)
        return

    # Divide one second evenly by the requested number of toggles. For example:
    # value 1 -> interval 1.0 s; value 2 -> 0.5 s; value 5 -> 0.2 s.
    interval = 1 / number_of_toggles

    # Wait half an interval before the first toggle. This centres the toggles
    # inside the one-second period. For value 1, it toggles exactly at 0.5 s.
    time.sleep(interval / 2)

    # Change the LED between HIGH and LOW the requested number of times.
    for toggle_number in range(number_of_toggles):
        # Read the current LED output and write its opposite state.
        GPIO.output(LED_PIN, not GPIO.input(LED_PIN))

        # Wait a full interval only when another toggle still needs to happen.
        if toggle_number < number_of_toggles - 1:
            time.sleep(interval)

    # The first and final half intervals together form one complete interval.
    # Combined with the waits inside the loop, the whole sequence lasts 1 s.
    time.sleep(interval / 2)


try:
    # Add an event to every BCD pin for both pressing and releasing.
    for pin in BCD_PINS:
        GPIO.add_event_detect(
            pin,
            GPIO.BOTH,  # Detect HIGH→LOW and LOW→HIGH changes.
            # RPi.GPIO automatically calls bcd_changed(pin) after an edge.
            callback=bcd_changed,
            bouncetime=50,  # Ignore button bounce for 50 ms.
        )

    # Report the value that was read before event detection started.
    if initial_value > 9:
        print(
            f"Invalid starting BCD input: "
            f"{initial_value:04b} ({initial_value}); using 0"
        )
    else:
        print(f"Starting BCD value: {bcd_value:04b} ({bcd_value})")

    while True:
        # The event callback may update bcd_value at any moment. Copy it before
        # starting so one LED sequence always uses one consistent value. A BCD
        # change during this second will be used at the start of the next second.
        current_value = bcd_value
        toggle_led(current_value)

except KeyboardInterrupt:
    # Ctrl+C is the normal safe way to leave the infinite loop.
    print("\nProgram stopped.")

finally:
    # This block runs after Ctrl+C and also after unexpected errors. Remove the
    # callbacks first, then return every GPIO pin to a safe input state.
    for pin in BCD_PINS:
        GPIO.remove_event_detect(pin)
    GPIO.cleanup()
