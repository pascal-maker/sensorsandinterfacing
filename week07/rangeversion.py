from time import sleep
from RPi import GPIO

GPIO.setmode(GPIO.BCM)

pins = (19, 13, 6, 5)

GPIO.setup(pins, GPIO.OUT)  # all pins at once

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

try:
    # Run forever.

    # Turn once in 1 direction
    for n in range(512):
        for step in steps:
            for i in range(4):
                GPIO.output(pins[i], step[i])

            sleep(0.001)  # Dictates how fast stepper motor will run

    # Turn once in the other direction
    for n in range(512):
        for step in steps:
            for i in range(4):
                GPIO.output(pins[3 - i], step[i])  # reverse

            sleep(0.001)  # Dictates how fast stepper motor will run

# Once finished clean everything up
except KeyboardInterrupt:
    print("cleanup")
    GPIO.cleanup()

finally:
    GPIO.cleanup()