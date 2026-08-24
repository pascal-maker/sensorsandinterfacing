"""Control three LEDs with two active-LOW push buttons.

Button 1 cycles through four modes:
    0 -> all LEDs off
    1 -> LED 1 on
    2 -> LED 2 on
    3 -> LED 3 on

Button 2 has priority and flashes all three LEDs while it is held down.
"""

import time

from RPi import GPIO


# BCM pin numbers for the three LEDs.
LED1 = 9
LED2 = 10
LED3 = 11
LEDS = [LED1, LED2, LED3]

# BCM pin numbers for the two buttons.
BTN1 = 20
BTN2 = 21


# BCM numbering uses GPIO numbers instead of physical header-pin numbers.
GPIO.setmode(GPIO.BCM)

# Each LED pin is an output. Starting LOW ensures every LED begins off.
for led in LEDS:
    GPIO.setup(led, GPIO.OUT)
    GPIO.output(led, GPIO.LOW)

# The internal pull-up resistors keep the inputs HIGH when the buttons are not
# pressed. Pressing a button connects its pin to ground, so it reads LOW.
GPIO.setup(BTN1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BTN2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Mode 0 means off; modes 1, 2, and 3 select one of the three LEDs.
mode = 0

# Store Button 1's previous value so a held button counts as only one press.
previous_btn1_state = GPIO.input(BTN1)


def all_off():
    """Turn all three LEDs off."""
    print("Turning all LEDs off")
    for led in LEDS:
        GPIO.output(led, GPIO.LOW)


def show_mode():
    """Clear the LEDs and light the one selected by the current mode."""
    print(f"Showing mode: {mode}")
    all_off()

    if mode == 1:
        GPIO.output(LED1, GPIO.HIGH)
    elif mode == 2:
        GPIO.output(LED2, GPIO.HIGH)
    elif mode == 3:
        GPIO.output(LED3, GPIO.HIGH)


try:
    print("Program started. Press Ctrl+C to stop.")

    while True:
        # Read both button inputs once at the beginning of the loop.
        current_btn1_state = GPIO.input(BTN1)
        current_btn2_state = GPIO.input(BTN2)

        # Button 2 has priority. Because the input is active-LOW, LOW means
        # that the button is currently being held down.
        if current_btn2_state == GPIO.LOW:
            print("Button 2 held: flashing all LEDs")

            # Reading an output pin gives its current state. `not` reverses
            # that state, so every LED toggles between on and off.
            for led in LEDS:
                GPIO.output(led, not GPIO.input(led))

            # This is the flash interval, not the Button 1 debounce delay.
            time.sleep(0.3)

            # If Button 2 was released during the delay, finish with LEDs off.
            if GPIO.input(BTN2) == GPIO.HIGH:
                all_off()

        else:
            # Detect a falling edge: Button 1 changed from HIGH to LOW.
            # This responds once when pressed instead of repeatedly while held.
            button1_just_pressed = (
                previous_btn1_state == GPIO.HIGH
                and current_btn1_state == GPIO.LOW
            )

            if button1_just_pressed:
                # Wait for the mechanical contacts to stop bouncing.
                time.sleep(0.05)

                # Confirm that the button is still pressed after debouncing.
                if GPIO.input(BTN1) == GPIO.LOW:
                    # Modulo cycles 0 -> 1 -> 2 -> 3 -> 0.
                    mode = (mode + 1) % 4
                    print(f"Button 1 pressed: changing to mode {mode}")
                    show_mode()

            # Save this reading for the next falling-edge comparison.
            previous_btn1_state = current_btn1_state

            # A short delay prevents this polling loop from using excessive CPU.
            time.sleep(0.01)

except KeyboardInterrupt:
    print("\nCtrl+C received. Stopping the program...")

finally:
    # The finally block always runs, including after Ctrl+C or another error.
    all_off()
    GPIO.cleanup()
    print("GPIO cleanup complete.")
