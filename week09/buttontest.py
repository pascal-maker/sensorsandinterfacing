import RPi.GPIO as GPIO
import time

BTN_UP = 20
BTN_DOWN = 21
BTN_LEFT = 26
BTN_RIGHT = 16
JOY_CLICK = 7

buttons = {
    "UP": BTN_UP,
    "DOWN": BTN_DOWN,
    "LEFT": BTN_LEFT,
    "RIGHT": BTN_RIGHT,
    "JOY": JOY_CLICK
}

GPIO.setmode(GPIO.BCM)

for pin in buttons.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        for name, pin in buttons.items():
            if GPIO.input(pin) == GPIO.LOW:
                print(name, "pressed")
                time.sleep(0.2)
except KeyboardInterrupt:
    GPIO.cleanup()