import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
pins = [16, 20, 21, 26]
for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
previous_value = None
try:
    while True:
        value = 0
        bits = []
        for i, pin in enumerate(pins):
            bit = 1 - GPIO.input(pin)
            bits.append(bit)
            value |= bit << i
        
        if value != previous_value:
            print(f"b0 = {bits[0]} b1 = {bits[1]} b2 = {bits[2]} b3 = {bits[3]}", end = " ")
            if value <= 9:
                print(f"BCD digit: {value}")
            else:
                print(f"Invalid BCD value: {value}")
            previous_value = value
        time.sleep(0.2)
except KeyboardInterrupt:
    GPIO.cleanup()