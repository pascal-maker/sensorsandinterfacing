"""Display raw Week 09 button and joystick-click input changes."""

import time

import RPi.GPIO as GPIO


PINS = {
    "UP": 20,
    "DOWN": 21,
    "LEFT": 26,
    "RIGHT": 16,
    "JOY": 7,
}


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    for pin in PINS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    print("Week 09 input test started")
    print("Press and release each control. Press Ctrl+C to stop.")
    print("Released should be 1; pressed should be 0.")

    previous = None

    try:
        while True:
            current = {name: GPIO.input(pin) for name, pin in PINS.items()}

            # Print only when at least one electrical input changes.
            if current != previous:
                values = " ".join(
                    f"{name}={value}" for name, value in current.items()
                )
                print(values)
                previous = current

            time.sleep(0.02)
    except KeyboardInterrupt:
        print("\nInput test stopped")
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    main()
