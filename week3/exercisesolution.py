import RPi.GPIO as GPIO
import time
import threading

# --- Pins ---
# 4 BCD input pins: bit values 1, 2, 4, 8
BCD_PINS = [16, 20, 21, 26]

# LED output pin
LED_PIN = 17

# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Set LED pin as output
GPIO.setup(LED_PIN, GPIO.OUT)

# Start with LED ON
GPIO.output(LED_PIN, GPIO.HIGH)

# Set all BCD pins as input with pull-up resistors
# Pull-up means:
# - normal state = 1
# - active / connected to GND = 0
for pin in BCD_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Shared variable that stores the latest BCD value
bcd_value = 0

# Lock to safely share bcd_value between callback thread and main loop
lock = threading.Lock()


def read_bcd():
    """
    Read the 4 BCD input pins and combine them into one number.
    Example:
    bit0=1, bit1=0, bit2=1, bit3=0 -> 0101 -> 5
    """
    value = 0

    # enumerate gives:
    # i = 0,1,2,3  (bit position)
    # pin = actual GPIO number
    for i, pin in enumerate(BCD_PINS):
        # Read pin and invert it because of pull-up logic
        # Pull-up gives:
        #   not active = 1
        #   active     = 0
        # We want:
        #   active     = 1
        #   not active = 0
        bit = 1 - GPIO.input(pin)

        # Put the bit in the correct place and add it to value
        value |= bit << i

    return value


def bcd_changed(channel):
    """
    Callback function.
    This runs automatically whenever one of the BCD pins changes.
    """
    global bcd_value

    # Read the full 4-bit BCD value again
    new_value = read_bcd()

    # Store it safely because callback runs in another thread
    with lock:
        bcd_value = new_value

    # Print the new value for debugging
    if new_value <= 9:
        print(f"BCD changed -> {new_value}")
    else:
        print(f"Invalid BCD value -> {new_value}")


# Add event detection to all 4 BCD pins
# GPIO.BOTH means react to both rising and falling edges
# bouncetime helps ignore noisy bounce signals
for pin in BCD_PINS:
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=bcd_changed, bouncetime=50)

# Read initial BCD value once at startup
bcd_value = read_bcd()
print(f"Start BCD value: {bcd_value}")

try:
    while True:
        # Safely copy the current BCD value
        with lock:
            value = bcd_value

        # Only valid BCD digits 0..9
        if 0 <= value <= 9:

            # If value is 0: do not toggle LED, just wait 1 second
            if value == 0:
                time.sleep(1)

            else:
                # Spread the toggles evenly over 1 second
                # Example:
                # value = 1 -> delay = 1/2 = 0.5
                # value = 2 -> delay = 1/3
                delay = 1 / (value + 1)

                # Toggle the LED 'value' times
                for _ in range(value):
                    time.sleep(delay)

                    # Toggle LED:
                    # if ON -> OFF
                    # if OFF -> ON
                    GPIO.output(LED_PIN, not GPIO.input(LED_PIN))

                # Final wait so total cycle is 1 second
                time.sleep(delay)

        else:
            # If BCD is invalid (10..15), print error and wait
            print(f"Invalid BCD value: {value}")
            time.sleep(1)

# Stop safely with Ctrl+C
except KeyboardInterrupt:
    # Remove event detection from all BCD pins
    for pin in BCD_PINS:
        GPIO.remove_event_detect(pin)

    # Reset GPIO cleanly
    GPIO.cleanup()
    
    ##We use the callback function to update the BCD value whenever one of the BCD input pins changes, so the Pi knows the new value immediately without constant polling. The lock is there because both the callback and the while loop use bcd_value, so it makes sure only one of them accesses or changes it at a time.