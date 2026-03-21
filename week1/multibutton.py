import RPi.GPIO as GPIO
import time

# LED is connected to GPIO17
LED = 17

# Define the GPIO pins for the four buttons
BTN_BOTTOM = 20   # Bottom button -> LED off
BTN_TOP = 21      # Top button -> LED on
BTN_LEFT = 26     # Left button -> slow blink
BTN_RIGHT = 16    # Right button -> fast blink

# Use BCM numbering (GPIO numbers, not physical board pin numbers)
GPIO.setmode(GPIO.BCM)

# Set the LED pin as an output
GPIO.setup(LED, GPIO.OUT)

# Set each button pin as an input with an internal pull-up resistor
# This means:
# - not pressed = 1
# - pressed = 0
GPIO.setup(BTN_BOTTOM, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_TOP, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_LEFT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN_RIGHT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Start with the LED in "off" mode
mode = "off"

try:
    while True:
        # Check if the bottom button is pressed
        # If yes, set mode to "off"
        if GPIO.input(BTN_BOTTOM) == 0:
            mode = "off"
            print("Mode: Off")
            time.sleep(0.2)  # Small delay for debounce

        # Check if the top button is pressed
        # If yes, set mode to "on"
        elif GPIO.input(BTN_TOP) == 0:
            mode = "on"
            print("Mode: On")
            time.sleep(0.2)  # Small delay for debounce

        # Check if the left button is pressed
        # If yes, set mode to "slow"
        elif GPIO.input(BTN_LEFT) == 0:
            mode = "slow"
            print("Mode: Slow")
            time.sleep(0.2)  # Small delay for debounce

        # Check if the right button is pressed
        # If yes, set mode to "fast"
        elif GPIO.input(BTN_RIGHT) == 0:
            mode = "fast"
            print("Mode: Blink Fast")
            time.sleep(0.2)  # Small delay for debounce

        # Perform the action that belongs to the current mode

        # OFF mode: send LOW to LED pin, so LED is off
        if mode == "off":
            GPIO.output(LED, GPIO.LOW)
            time.sleep(0.05)

        # ON mode: send HIGH to LED pin, so LED stays on
        elif mode == "on":
            GPIO.output(LED, GPIO.HIGH)
            time.sleep(0.05)

        # SLOW mode: LED blinks slowly
        elif mode == "slow":
            GPIO.output(LED, GPIO.HIGH)  # LED on
            time.sleep(0.5)
            GPIO.output(LED, GPIO.LOW)   # LED off
            time.sleep(0.5)

        # FAST mode: LED blinks quickly
        elif mode == "fast":
            GPIO.output(LED, GPIO.HIGH)  # LED on
            time.sleep(0.1)
            GPIO.output(LED, GPIO.LOW)   # LED off
            time.sleep(0.1)

# If user presses Ctrl + C, stop the loop
except KeyboardInterrupt:
    pass

# Always clean up GPIO pins before exiting
finally:
    GPIO.cleanup()

#The script defines one LED pin and four button pins.
# Each button is set up as an input with an internal pull-up resistor,
# so the button readings are stable and do not float. The LED pin is set up as an output.
# Inside an infinite loop, the script checks which button is pressed.
# Depending on the button, it changes the mode to off, on, slow blink, or fast blink.
# After that, the script performs the selected mode by sending either GPIO.HIGH or GPIO.LOW to the LED. 
# In slow and fast mode, it alternates between HIGH and LOW with different delays to make the LED blink. The program keeps running until it is stopped,
# after which GPIO.cleanup()
# resets the GPIO pins.