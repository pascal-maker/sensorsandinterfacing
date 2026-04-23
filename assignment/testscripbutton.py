import time
import RPi.GPIO as GPIO

PINS = [17, 27, 14]

GPIO.setmode(GPIO.BCM)

for pin in PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

last = {pin: GPIO.input(pin) for pin in PINS}

print("Press ONLY the 4th button...")

try:
    while True:
        for pin in PINS:
            current = GPIO.input(pin)
            if current != last[pin]:
                print(f"GPIO {pin} changed: {last[pin]} -> {current}")
                last[pin] = current
        time.sleep(0.05)

except KeyboardInterrupt:
    GPIO.cleanup()