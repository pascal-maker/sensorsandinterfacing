from RPi import GPIO
import time


# The list order determines each input's binary weight:
# GPIO 16 = 1, GPIO 20 = 2, GPIO 21 = 4, GPIO 26 = 8.
BCD_PINS = [16, 20, 21, 26]
LED_PIN = 17

GPIO.setmode(GPIO.BCM)

# The BCD inputs are active-low, so every reading must be inverted.
for pin in BCD_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.HIGH)


def read_bcd():
    """Read the four inputs and combine them into one four-bit value."""
    value = 0

    # enumerate() gives the bit position (0-3) and its GPIO pin.
    for bit_position, pin in enumerate(BCD_PINS):
        raw_bit = GPIO.input(pin)  # Read HIGH (1) or LOW (0).
        inverted_bit = raw_bit ^ 1  # Active-low: change 0 ↔ 1.

        # Shift the bit into position, then OR it into the nibble.
        value |= inverted_bit << bit_position

    # Send the completed nibble back to the caller.
    return value


# Read the real input value at startup instead of assuming it is zero.
initial_value = read_bcd()
bcd_value = initial_value if initial_value <= 9 else 0


def bcd_changed(channel):
    """Update the BCD value whenever one of the four inputs changes."""
    global bcd_value

    new_value = read_bcd()

    # A single BCD digit may contain only a value from 0 through 9.
    if new_value > 9:
        print(f"Invalid BCD input: {new_value:04b} ({new_value})")
        return

    bcd_value = new_value
    print(
        f"GPIO {channel} changed -> "
        f"BCD: {bcd_value:04b}, decimal: {bcd_value}"
    )


def toggle_led(number_of_toggles):
    """Toggle the LED the requested number of times in one second."""
    if number_of_toggles == 0:
        # For BCD zero, the LED remains on for the complete second.
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(1)
        return

    # Divide one second evenly between the requested toggles.
    interval = 1 / number_of_toggles

    # Starting halfway makes value 1 toggle at 0.5 seconds.
    time.sleep(interval / 2)

    # Change the LED between HIGH and LOW the requested number of times.
    for toggle_number in range(number_of_toggles):
        GPIO.output(LED_PIN, not GPIO.input(LED_PIN))

        # Use a full interval between toggles and half after the last one.
        if toggle_number < number_of_toggles - 1:
            time.sleep(interval)

    time.sleep(interval / 2)


try:
    # Add an event to every BCD pin for both pressing and releasing.
    for pin in BCD_PINS:
        GPIO.add_event_detect(
            pin,
            GPIO.BOTH,  # Detect HIGH→LOW and LOW→HIGH changes.
            callback=bcd_changed,  # Run after an input change.
            bouncetime=50,  # Ignore button bounce for 50 ms.
        )

    if initial_value > 9:
        print(
            f"Invalid starting BCD input: "
            f"{initial_value:04b} ({initial_value}); using 0"
        )
    else:
        print(f"Starting BCD value: {bcd_value:04b} ({bcd_value})")

    while True:
        # Take a snapshot so a callback cannot alter this one-second sequence.
        current_value = bcd_value
        toggle_led(current_value)

except KeyboardInterrupt:
    print("\nProgram stopped.")

finally:
    # Always stop event detection and release all GPIO pins safely.
    for pin in BCD_PINS:
        GPIO.remove_event_detect(pin)
    GPIO.cleanup()
