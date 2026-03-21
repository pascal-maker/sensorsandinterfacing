import time
from RPi import GPIO

# Define GPIO pins for the traffic lights
GREEN = 9
YELLOW = 10
RED = 11

# Use BCM pin numbering
GPIO.setmode(GPIO.BCM)

# Set all traffic light pins as output pins
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(YELLOW, GPIO.OUT)
GPIO.setup(RED, GPIO.OUT)

# Function to set the traffic lights
# True = LED on
# False = LED off
def set_lights(green, yellow, red):
    GPIO.output(GREEN, green)
    GPIO.output(YELLOW, yellow)
    GPIO.output(RED, red)

try:
    while True:
        # Turn green light on, yellow and red off
        set_lights(True, False, False)
        print("GREEN")
        time.sleep(5)

        # Turn yellow light on, green and red off
        set_lights(False, True, False)
        print("YELLOW")
        time.sleep(1)

        # Turn red light on, green and yellow off
        set_lights(False, False, True)
        print("RED")
        time.sleep(5)

# Stop program safely if Ctrl+C is pressed
except KeyboardInterrupt:
    pass

# Always reset GPIO pins at the end
finally:
    GPIO.cleanup()