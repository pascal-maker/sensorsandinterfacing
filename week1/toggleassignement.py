import RPi.GPIO as GPIO
import time

btn = 20                  # Button is connected to GPIO20
led = 17                  # LED is connected to GPIO17

GPIO.setmode(GPIO.BCM)    # Use BCM pin numbering
GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button as input with pull-up resistor
GPIO.setup(led, GPIO.OUT) # LED as output

led_state = False         # Start with LED off
previous_btn_state = GPIO.input(btn)  # Remember the button's initial state

try:
    while True:
        current_btn_state = GPIO.input(btn)  # Read the button's current state

        # Detect a new button press:
        # previous state was 1 (not pressed)
        # current state is 0 (pressed)
        if previous_btn_state == 1 and current_btn_state == 0:
            led_state = not led_state        # Flip LED state: off->on or on->off
            GPIO.output(led, led_state)      # Apply the new LED state
            print(f"Button pressed -> LED is now {'ON' if led_state else 'OFF'}")
            time.sleep(0.2)                  # Small delay to avoid button bounce

        previous_btn_state = current_btn_state  # Save current state for next loop
        time.sleep(0.01)                       # Tiny pause to reduce CPU usage

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()         # Reset all GPIO pins when program stops
    

#The program uses led_state to remember whether the LED is on or off.
#It stores the previous button state and compares it with the current button state.
#When the button changes from 1 to 0, this means the button was pressed, so the LED state is toggled.    