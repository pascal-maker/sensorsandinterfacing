from time import sleep
from RPi import GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pins = (19, 13, 6, 5)

GPIO.setup(pins, GPIO.OUT)

steps = (
    (1, 0, 0, 0),  # Orange
    (1, 1, 0, 0),  # Orange + Yellow
    (0, 1, 0, 0),  # Yellow
    (0, 1, 1, 0),  # Yellow + Pink
    (0, 0, 1, 0),  # Pink
    (0, 0, 1, 1),  # Pink + Blue
    (0, 0, 0, 1),  # Blue
    (1, 0, 0, 1),  # Blue + Orange
)

try:
    while True:
        for step in steps:
            for i in range(4):
                GPIO.output(pins[i], step[i])
            sleep(0.02)

except KeyboardInterrupt:
    GPIO.cleanup()       