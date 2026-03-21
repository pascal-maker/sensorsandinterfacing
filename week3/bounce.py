import RPi.GPIO as GPIO
import time

BUTTON_PIN = 20
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def button_callback(channel): # Define a callback function to be called when the button is pressed
    print(f"Button pressed on GPIO {channel}!") # Define a callback function to be called when the button is pressed

GPIO.add_event_detect(BUTTON_PIN,
                      GPIO.FALLING, # Set up event detection for the button pin on the falling edge (button press)
                      callback=button_callback, # Set up event detection for the button pin on the falling edge (button press)
                      bouncetime=200)  # Set up event detection for the button pin with a debounce time of 200 ms

try:
    print("Waiting for button presses. Press Ctrl+C to exit.")  
    while True:
        print("Main loop is running...")
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.remove_event_detect(BUTTON_PIN)
    GPIO.cleanup()        
    
    
# This script uses interrupt-based edge detection instead of polling.
# GPIO watches the button pin in the background and runs the callback
# when a falling edge is detected. Bouncetime is used to debounce the button.    