from RPi import GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

# GPIO pins connected to IN1, IN2, IN3, IN4
pins = (19, 13, 6, 5)

GPIO.setup(pins, GPIO.OUT)

# 8-step half-step sequence
steps = (
    (1, 0, 0, 0),  # step 1
    (1, 1, 0, 0),  # step 2
    (0, 1, 0, 0),  # step 3
    (0, 1, 1, 0),  # step 4
    (0, 0, 1, 0),  # step 5
    (0, 0, 1, 1),  # step 6
    (0, 0, 0, 1),  # step 7
    (1, 0, 0, 1),  # step 8
)

def apply_step(step):
    for i in range(4):
        GPIO.output(pins[i], step[i])

def stop_motor():
    for pin in pins:
        GPIO.output(pin, 0)

try:
    print("Clockwise")
    for _ in range(512):
        for step in steps:
            apply_step(step)
            sleep(0.001)

    print("Counterclockwise")
    for _ in range(512):
        for step in reversed(steps):
            apply_step(step)
            sleep(0.001)

    stop_motor()

except KeyboardInterrupt:
    stop_motor()

finally:
    GPIO.cleanup()