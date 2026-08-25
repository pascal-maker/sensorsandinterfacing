"""Practice Exam 6 starter — implement the state machine yourself."""

import os
import time

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import RPi.GPIO as GPIO

from exams.copy_paste_kit.active_buzzer import ActiveBuzzer
from exams.copy_paste_kit.csv_logger import CSVLogger
from exams.copy_paste_kit.keypad_4x4 import Keypad4x4
from exams.copy_paste_kit.servo_motor import ServoMotor


SECRET_CODE = "2580"


def code_is_correct(entry):
    # TODO: return whether entry matches SECRET_CODE.
    raise NotImplementedError


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    keypad = Keypad4x4()
    servo = ServoMotor(pin=18)
    buzzer = ActiveBuzzer(pin=23)
    logger = CSVLogger(
        "access_attempts.csv",
        ["result", "digits_entered", "failed_attempts"],
    )

    entry = ""
    failed_attempts = 0
    state = "LOCKED"
    deadline = None
    servo.set_angle(0)

    try:
        while True:
            now = time.monotonic()
            key = keypad.get_key()

            # TODO: handle lockout and unlock deadlines without blocking.
            # TODO: handle digits, *, and # according to assignment.md.
            # TODO: log result and digit count, but never log entry itself.
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Practice stopped")
    finally:
        servo.set_angle(0)
        servo.release()
        buzzer.cleanup()
        keypad.cleanup()
        logger.close()
        servo.cleanup()
        GPIO.cleanup()


if __name__ == "__main__":
    main()
