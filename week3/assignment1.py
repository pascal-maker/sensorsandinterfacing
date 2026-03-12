import RPi.GPIO as GPIO
import time

# Use BCM numbering, so we refer to GPIO pins by their BCM number
GPIO.setmode(GPIO.BCM)

# These 4 pins represent the 4 BCD bits:
# 16 = bit 0 = value 1
# 20 = bit 1 = value 2
# 21 = bit 2 = value 4
# 26 = bit 3 = value 8
pins = [16, 20, 21, 26]

# Set every pin as input with an internal pull-up resistor
# That means:
# - normal state = 1
# - pressed / connected to GND = 0
for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# We use this to remember the last value,
# so we only print when the value changes
previous_value = None

try:
    # Keep checking the inputs forever
    while True:
        # Start from 0 each loop and rebuild the BCD value from scratch
        value = 0

        # enumerate(pins) gives:
        # i = bit position (0,1,2,3)
        # pin = actual GPIO pin number
        for i, pin in enumerate(pins):
            # Read the pin and invert it
            # Because with pull-up:
            #   not pressed = 1
            #   pressed     = 0
            # We want:
            #   pressed     = 1
            #   not pressed = 0
            bit = 1 - GPIO.input(pin)

            # Put the bit in the correct position and add it to value
            # Example:
            # if bit = 1 and i = 2, then 1 << 2 = 4
            value |= bit << i

        # BCD is only valid for decimal digits 0 to 9
        if value <= 9:
            # Only print when the value changes
            if value != previous_value:
                print(f"BCD digit: {value}")
                previous_value = value
        else:
            # If the value is 10-15, it is not valid BCD
            if value != previous_value:
                print(f"Invalid BCD value: {value}")
                previous_value = value

        # Small delay so the loop does not run too fast
        time.sleep(0.2)

# Stop safely with Ctrl+C
except KeyboardInterrupt:
    GPIO.cleanup()

#First we choose the pins 16, 20, 21, and 26. These are our 4 BCD inputs. Then we use GPIO.setup to make them input pull-up pins. That means they are normally 1, and when pressed they become 0.
#Then while True keeps the program running forever.
#Inside the loop we reset value to 0, because we want to build the digit again from scratch.
#Then we loop over the 4 pins. For each pin we read its input and invert it with 1 - GPIO.input(pin) so that pressed becomes 1 and not pressed becomes 0.
#Then we put each bit in the correct place with bit << i and add it to value using |=.
#After that, if value <= 9, it is a valid BCD digit. If it is different from the previous value, we print it. If it is bigger than 9, it is not a valid BCD number.                   