"""Practice Exam 6 solution: keypad servo lock with alarm and lockout."""

import math
import os
import time
from enum import Enum, auto

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO

# Reusable exam-kit classes contain the low-level hardware operations.
from exams.copy_paste_kit.active_buzzer import ActiveBuzzer
from exams.copy_paste_kit.csv_logger import CSVLogger
from exams.copy_paste_kit.keypad_4x4 import Keypad4x4
from exams.copy_paste_kit.servo_motor import ServoMotor


# Hardware pins, angles, durations, and security limits are defined in one place.
SECRET_CODE = "2580"
SERVO_PIN = 18
BUZZER_PIN = 23
LOCKED_ANGLE = 0
UNLOCKED_ANGLE = 90
UNLOCK_SECONDS = 5.0
LOCKOUT_SECONDS = 15.0
MAX_FAILURES = 3


class LockState(Enum):
    """Every valid operating state of the keypad lock."""

    LOCKED = auto()
    UNLOCKED = auto()
    LOCKOUT = auto()


def code_is_correct(entry):
    """Keep validation separate and never pass the entered code to the logger."""
    return entry == SECRET_CODE


def main():
    """Run the non-blocking keypad-lock state machine until Ctrl+C."""
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    # Keypad4x4 scans columns and debounces keys so a held key is returned once.
    keypad = Keypad4x4(
        row_pins=(16, 20, 21, 26),
        column_pins=(19, 13, 6, 5),
    )
    servo = ServoMotor(pin=SERVO_PIN)
    buzzer = ActiveBuzzer(pin=BUZZER_PIN)
    # The log intentionally stores only the result and number of entered digits.
    # Neither the entered value nor SECRET_CODE is passed to CSVLogger.
    logger = CSVLogger(
        "access_attempts.csv",
        ["timestamp", "result", "digits_entered", "failed_attempts"],
    )

    # Application state is kept separately from the hardware driver objects.
    entry = ""
    failed_attempts = 0
    state = LockState.LOCKED
    deadline = None
    last_reported_seconds = None
    # Begin in the safe physical state before accepting any keypad input.
    servo.set_angle(LOCKED_ANGLE)

    print("Keypad servo lock started")
    print("Enter four digits, * clears, and # submits.")

    try:
        while True:
            now = time.monotonic()

            # Deadline checks are non-blocking, so the loop stays responsive.
            if state is LockState.UNLOCKED and now >= deadline:
                # The five-second deadline expired, so lock without blocking.
                servo.set_angle(LOCKED_ANGLE)
                state = LockState.LOCKED
                deadline = None
                print("Servo relocked")

            if state is LockState.LOCKOUT:
                if now >= deadline:
                    # A completed lockout resets the consecutive-failure count.
                    state = LockState.LOCKED
                    deadline = None
                    failed_attempts = 0
                    last_reported_seconds = None
                    print("Lockout ended")
                else:
                    # ceil() shows whole remaining seconds. Comparing with the
                    # last value limits console output to at most once per second.
                    remaining = math.ceil(deadline - now)
                    if remaining != last_reported_seconds:
                        print(f"LOCKOUT: {remaining} seconds remaining")
                        last_reported_seconds = remaining

                # Scan to consume/release held keys, but ignore their values.
                # Reading and discarding input lets Keypad4x4 track releases,
                # while ensuring lockout key presses never affect the entry.
                keypad.get_key()
                time.sleep(0.01)
                continue

            # get_key() returns a key once per press or None if nothing is new.
            key = keypad.get_key()
            if key is None:
                time.sleep(0.01)
                continue

            # Ignore all keypad commands while temporarily unlocked.
            if state is LockState.UNLOCKED:
                continue

            if key.isdigit():
                # Accept no more than the required four digits.
                if len(entry) < 4:
                    entry += key
                    print("Entry:", "*" * len(entry))

            elif key == "*":
                entry = ""
                print("Entry cleared")

            elif key == "#":
                # Save only the length before clearing the private entry later.
                digits_entered = len(entry)

                if code_is_correct(entry):
                    # A successful attempt clears previous failures and starts
                    # a five-second unlock deadline without sleeping for it.
                    failed_attempts = 0
                    state = LockState.UNLOCKED
                    deadline = now + UNLOCK_SECONDS
                    servo.set_angle(UNLOCKED_ANGLE)
                    logger.write("success", digits_entered, failed_attempts)
                    print("Access granted: servo unlocked for 5 seconds")
                else:
                    # Log the updated consecutive-failure count, then signal the
                    # failed attempt with two short active-buzzer beeps.
                    failed_attempts += 1
                    logger.write("failure", digits_entered, failed_attempts)
                    print(f"Access denied ({failed_attempts}/{MAX_FAILURES})")
                    buzzer.beep(duration=0.12, count=2, gap=0.10)

                    if failed_attempts >= MAX_FAILURES:
                        # The alarm is followed by a timed state in which all
                        # keypad input is read but ignored.
                        buzzer.beep(duration=1.0)
                        state = LockState.LOCKOUT
                        deadline = time.monotonic() + LOCKOUT_SECONDS
                        last_reported_seconds = None
                        print("Too many failures: 15-second lockout")

                # Always discard an entry immediately after it is submitted.
                entry = ""

            # A-D deliberately have no branch and are therefore ignored.
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nPractice Exam 6 stopped")
    finally:
        # Return every output to its safe state even after an unexpected error.
        servo.set_angle(LOCKED_ANGLE)
        time.sleep(0.3)
        servo.release()
        buzzer.cleanup()
        keypad.cleanup()
        logger.close()
        servo.cleanup()
        GPIO.cleanup()
        print("Servo locked; buzzer, keypad, CSV, and GPIO cleaned up")


if __name__ == "__main__":
    main()
