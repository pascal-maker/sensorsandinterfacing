from time import sleep
from RPi import GPIO

GPIO.setmode(GPIO.BCM)

pins = (19, 13, 6, 5)

GPIO.setup(pins, GPIO.OUT)

steps = (
    (1, 0, 0, 0),
    (1, 1, 0, 0),
    (0, 1, 0, 0),
    (0, 1, 1, 0),
    (0, 0, 1, 0),
    (0, 0, 1, 1),
    (0, 0, 0, 1),
    (1, 0, 0, 1),
)

try:
    while True:
        for step in steps:
            for i in range(4):
                GPIO.output(pins[i], step[i])
            sleep(0.001)

except KeyboardInterrupt:
    print("cleanup")

finally:
    GPIO.cleanup()