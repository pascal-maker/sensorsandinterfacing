import RPi.GPIO as GPIO   # Library to talk to the Pi's pins
import time               # Library to handle time and delays

# Use the BCM pin numbering (the numbers printed on most cobblers/diagrams)
GPIO.setmode(GPIO.BCM)   

# These are the pins for your 4 buttons (weighted 1, 2, 4, 8)
pins = [16, 20, 21, 26]
# The pin connected to your LED
LED = 17

# --- Global variables ---
current_value = 0      # This stores the current decimal number (0-9)
last_toggle = time.time() # Keeps track of the exact time the LED last switched
led_state = True       # Tracks if the LED is currently ON (True) or OFF (False)


def read_bcd():
    """
    Reads the physical state of the 4 buttons and 
    converts that binary pattern into a decimal number.
    """
    value = 0
    bits = []

    for i in range(4):
        # We use 'not' because PULL_UP means:
        # Button NOT pressed = 1 (True)
        # Button PRESSED = 0 (False)
        # Inverting it makes Pressed = 1, which is easier to code.
        bit = int(not GPIO.input(pins[i])) 
        bits.append(bit)
        
        # Binary math: Shift the bit to its correct position (1, 2, 4, or 8)
        # and add it to our total value using bitwise OR.
        value |= bit << i

    return value, bits


# --- Setup Hardware ---
for pin in pins:
    # Set buttons as input with internal pull-up resistors
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set LED as output
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, led_state)


def bcd_callback(channel):
    """
    This function runs AUTOMATICALLY whenever a button is pressed or released.
    This is the "Event" the assignment asked for.
    """
    global current_value

    # Update our global current_value based on the new button states
    value, bits = read_bcd()
    current_value = value

    # Print status to the console so we can debug
    print(f"bit 0 = {bits[0]} | bit 1 = {bits[1]} | bit 2 = {bits[2]} | bit 3 = {bits[3]}")
    print(f"BCD value = {current_value}")
    print("----")


# Tell the Pi to watch for "Events" (changes) on all 4 BCD pins.
# 'BOTH' means it triggers when you press AND when you release.
for pin in pins:
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=bcd_callback, bouncetime=200)

# Run once at start to see what the buttons are doing before we begin
current_value, _ = read_bcd()

try:
    while True:
        now = time.time() # Get the current clock time

        if current_value == 0:
            # Per assignment: If value is 0, keep LED on (no blinking)
            led_state = True
            GPIO.output(LED, led_state)
        else:
            # Calculate how long to wait between toggles.
            # Example: If value is 2, interval is 0.5 seconds (blinks twice per sec)
            interval = 1 / current_value

            # Check if enough time has passed since the last toggle
            if now - last_toggle >= interval:
                led_state = not led_state  # Flip the state (True -> False or vice versa)
                GPIO.output(LED, led_state)
                last_toggle = now          # Reset the timer for the next blink

        # Small sleep to keep the CPU from running at 100% usage
        time.sleep(0.01)

except KeyboardInterrupt:
    # Clean exit if you press Ctrl+C
    print("Exiting...")

finally:
    # Reset pins to a safe state (turns LED off)
    GPIO.cleanup() 