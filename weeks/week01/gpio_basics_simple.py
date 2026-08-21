"""Simple GPIO demo using functions instead of classes.

Buttons:
    GPIO 20 -> LED on
    GPIO 21 -> LED off
    GPIO 16 -> blink fast
    GPIO 26 -> blink slow

LED:
    GPIO 17
"""

import time

import RPi.GPIO as GPIO


# BCM pin numbers used by the circuit.
LED_PIN = 17
ON_BUTTON = 20
OFF_BUTTON = 21
FAST_BUTTON = 16
SLOW_BUTTON = 26


def setup_gpio():
    """Configure the LED and four active-LOW buttons."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    GPIO.setup(LED_PIN, GPIO.OUT, initial=GPIO.LOW)

    for button_pin in (ON_BUTTON, OFF_BUTTON, FAST_BUTTON, SLOW_BUTTON):
        GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    print("GPIO setup complete.")


def button_pressed(pin):
    """Return True while an active-LOW button is pressed."""
    return GPIO.input(pin) == GPIO.LOW


def set_led(is_on):
    """Switch the LED on or off."""
    GPIO.output(LED_PIN, GPIO.HIGH if is_on else GPIO.LOW)


def toggle_led():
    """Reverse the LED's current state."""
    current_state = GPIO.input(LED_PIN)
    GPIO.output(LED_PIN, not current_state)
    print(f"LED: {'OFF' if current_state else 'ON'}")


def choose_mode(current_mode):
    """Return a new mode when a button is pressed."""
    if button_pressed(ON_BUTTON):
        return "on"
    if button_pressed(OFF_BUTTON):
        return "off"
    if button_pressed(FAST_BUTTON):
        return "blink_fast"
    if button_pressed(SLOW_BUTTON):
        return "blink_slow"
    return current_mode


def perform_mode(mode):
    """Perform one step of the selected LED mode."""
    if mode == "on":
        set_led(True)
        time.sleep(0.05)
    elif mode == "off":
        set_led(False)
        time.sleep(0.05)
    elif mode == "blink_fast":
        toggle_led()
        time.sleep(0.1)
    elif mode == "blink_slow":
        toggle_led()
        time.sleep(0.5)


def main():
    setup_gpio()
    mode = "off"
    previous_mode = None

    print("Demo started. Press Ctrl+C to stop safely.")
    print("GPIO 20=ON | GPIO 21=OFF | GPIO 16=FAST | GPIO 26=SLOW")

    try:
        while True:
            mode = choose_mode(mode)

            if mode != previous_mode:
                print(f"Mode: {previous_mode or 'startup'} -> {mode}")
                previous_mode = mode

            perform_mode(mode)

    except KeyboardInterrupt:
        print("\nCtrl+C received. Stopping the demo...")
    finally:
        set_led(False)
        GPIO.cleanup()
        print("GPIO cleanup complete. Program ended safely.")


if __name__ == "__main__":
    main()
