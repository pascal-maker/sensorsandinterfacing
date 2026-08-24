"""Run a repeating three-LED traffic-light sequence."""

import time

from RPi import GPIO


# BCM GPIO pin numbers for the traffic-light LEDs.
GREEN = 9
YELLOW = 10
RED = 11
LEDS = [GREEN, YELLOW, RED]


# Use BCM GPIO numbering rather than physical header-pin numbering.
GPIO.setmode(GPIO.BCM)

# Configure every LED pin as an output and make sure it starts off.
for led in LEDS:
    GPIO.setup(led, GPIO.OUT, initial=GPIO.LOW)


def all_off():
    """Turn off every traffic-light LED."""
    for led in LEDS:
        GPIO.output(led, GPIO.LOW)


def show_light(led, name, duration):
    """Turn on one traffic light for a specified number of seconds."""
    # Clear the previous light before switching on the next one.
    all_off()
    GPIO.output(led, GPIO.HIGH)
    print(f"{name} light is ON for {duration} second(s)")
    time.sleep(duration)


try:
    print("Traffic light started. Press Ctrl+C to stop.")

    while True:
        show_light(GREEN, "Green", 5)
        show_light(YELLOW, "Yellow", 1)
        show_light(RED, "Red", 4)

except KeyboardInterrupt:
    print("\nCtrl+C received. Traffic light stopped.")

finally:
    # Leave the circuit in a safe state even if an error interrupts the loop.
    all_off()
    GPIO.cleanup()
    print("All LEDs are off. GPIO cleanup complete.")
