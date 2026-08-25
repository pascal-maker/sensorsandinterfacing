import RPi.GPIO as GPIO
import time

# Set the GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Define the GPIO pin number
button_pin = 20

# Set the GPIO pin as an input pin
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

try:
    while True:
        # Check if the button is pressed
        if GPIO.input(button_pin) == GPIO.LOW:
            print("Button is pressed!")
        # Wait for a short period
        time.sleep(0.1)
except KeyboardInterrupt:
    # Clean up GPIO settings
    GPIO.cleanup()
    print("Program ended.")