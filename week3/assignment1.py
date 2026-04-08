import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

pins = [16, 20, 21, 26]

for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        for pin in pins:
            b0 = int(not GPIO.input(16))
            b1 = int(not GPIO.input(20))
            b2 = int(not GPIO.input(21))
            b3 = int(not GPIO.input(26))

            print(f"bit 0 = {b0}")
            print(f"bit 1 = {b1}")
            print(f"bit 2 = {b2}")
            print(f"bit 3 = {b3}")

            value = 0 
            if b0:
                value |= 1 << 0
            if b1:
                value |= 1 << 1
            if b2:
                value |= 1 << 2
            if b3:
                value |= 1 << 3
            print(f" BCD value = {value}")
            print("\n")
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()