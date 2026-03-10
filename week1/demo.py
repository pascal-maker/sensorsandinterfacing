import time
from RPi import GPIO

GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering

btn = 20
led = 17

GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Button as input with pull-up resistor
GPIO.setup(led, GPIO.OUT)  # LED as output

try:
    while True:
        value = GPIO.input(btn)  # Read button state
        GPIO.output(led, not value)  # LED gets opposite value of button
        print('Button value: {0}, LED value: {1}'.format(value, not value))  # Show values
        time.sleep(0.5)  # Wait a little before checking again

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()  # Reset GPIO pins