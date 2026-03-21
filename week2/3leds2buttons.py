import RPi.GPIO as GPIO
import time

# Define the GPIO pins for the 3 LEDs
LED1 = 9     # First LED
LED2 = 10    # Second LED
LED3 = 11    # Third LED

# Define the GPIO pins for the 2 buttons
BTN1 = 20    # Button 1: cycle through LEDs
BTN2 = 21    # Button 2: toggle all LEDs while held

# Use BCM pin numbering
GPIO.setmode(GPIO.BCM)

# Set LED pins as output pins
GPIO.setup(LED1, GPIO.OUT)
GPIO.setup(LED2, GPIO.OUT)
GPIO.setup(LED3, GPIO.OUT)

# Set button pins as input pins with internal pull-up resistors
# That means:
# not pressed = 1
# pressed = 0
GPIO.setup(BTN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# This variable remembers the cycle state for button 1
# 0 = all LEDs off
# 1 = LED1 on
# 2 = LED2 on
# 3 = LED3 on
cycle_state = 0

# Save the starting state of button 1
# This is needed for edge detection
previous_btn1_state = GPIO.input(BTN1)

# This variable remembers if all LEDs are currently on or off
# while button 2 is being held
all_toggle_state = False

# Save the current time
# This is used so the LEDs only toggle every 0.3 seconds
previous_btn2_toggle_time = time.time()

# Function to turn on the correct LED for the current cycle state
def set_cycle_leds(state):
    GPIO.output(LED1, state == 1)   # LED1 on only if state is 1
    GPIO.output(LED2, state == 2)   # LED2 on only if state is 2
    GPIO.output(LED3, state == 3)   # LED3 on only if state is 3

# Function to turn all LEDs on or off at the same time
def set_all_leds(state):
    GPIO.output(LED1, state)
    GPIO.output(LED2, state)
    GPIO.output(LED3, state)

# Start with the LEDs in the current cycle state
# Since cycle_state = 0, all LEDs start off
set_cycle_leds(cycle_state)

try:
    while True:
        # Read the current state of both buttons
        btn1_state = GPIO.input(BTN1)
        btn2_state = GPIO.input(BTN2)

        # If button 2 is being held down
        if btn2_state == 0:
            now = time.time()

            # Only toggle all LEDs if at least 0.3 seconds passed
            if now - previous_btn2_toggle_time >= 0.3:
                all_toggle_state = not all_toggle_state   # Switch on/off
                set_all_leds(all_toggle_state)            # Apply to all LEDs
                previous_btn2_toggle_time = now           # Save new toggle time

        else:
            # If button 2 is not pressed, return to normal cycle mode
            set_cycle_leds(cycle_state)

            # Edge detection for button 1:
            # previous = 1 means not pressed
            # current = 0 means pressed
            # So this detects one clean new press
            if previous_btn1_state == 1 and btn1_state == 0:
                cycle_state = (cycle_state + 1) % 4   # Go to next state
                set_cycle_leds(cycle_state)           # Update LEDs
                time.sleep(0.05)                      # Small debounce delay

        # Save current button 1 state for next loop
        previous_btn1_state = btn1_state

        # Small delay so the CPU is not overloaded
        time.sleep(0.01)

except KeyboardInterrupt:
    # Stop program safely when Ctrl+C is pressed
    pass

finally:
    # Reset GPIO pins when program ends
    GPIO.cleanup()

# This script controls three LEDs with two buttons.

# BTN1 is used to cycle through the LEDs. Each time BTN1 is pressed, the script changes cycle_state, which decides whether LED1, LED2, LED3, or no LED should be on.

#BTN2 has a different behavior. While BTN2 is held down, all three LEDs blink together. This is done by checking the time and toggling all LEDs every 0.3 seconds.

#When BTN2 is released, the LEDs return to the normal BTN1 cycle behavior.

#The script uses pull-up resistors for the buttons, so a pressed button reads 0 and an unpressed button reads 1. It also uses edge detection for BTN1, so the script only reacts once per press instead of repeating while the button is held down.    