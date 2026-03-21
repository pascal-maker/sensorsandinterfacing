import RPi.GPIO as GPIO
import time

# Define the GPIO pins for the traffic lights and pedestrian button
GREEN = 9       # Green traffic light LED
YELLOW = 10     # Yellow traffic light LED
RED = 11        # Red traffic light LED
PED_BTN = 20    # Pedestrian button

# Use BCM pin numbering
GPIO.setmode(GPIO.BCM)

# Set the traffic light pins as output pins
GPIO.setup(GREEN, GPIO.OUT)
GPIO.setup(YELLOW, GPIO.OUT)
GPIO.setup(RED, GPIO.OUT)

# Set the pedestrian button as an input with a pull-up resistor
# Not pressed = 1
# Pressed = 0
GPIO.setup(PED_BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Function to control the three traffic light LEDs
def set_lights(green, yellow, red):
    GPIO.output(GREEN, green)
    GPIO.output(YELLOW, yellow)
    GPIO.output(RED, red)

try:
    while True:
        pedestrian_requested = False   # Reset pedestrian request at the start of each cycle

        # Turn the green light on
        set_lights(True, False, False)
        print("GREEN")

        # Keep the green light on for up to 5 seconds
        # During that time, keep checking if the pedestrian button is pressed
        start_time = time.time()
        while time.time() - start_time < 5:
            if GPIO.input(PED_BTN) == 0:   # Button pressed
                pedestrian_requested = True
                print("Pedestrian button pressed")
                break                      # Leave the green phase early
            time.sleep(0.01)               # Small pause to reduce CPU usage

        # Switch to yellow light
        set_lights(False, True, False)
        print("YELLOW")
        time.sleep(1)                      # Keep yellow on for 1 second

        # Switch to red light
        set_lights(False, False, True)
        print("RED")
        time.sleep(5)                      # Keep red on for 5 seconds

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()   # Reset GPIO pins when the program stops