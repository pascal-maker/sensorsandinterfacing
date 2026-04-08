import RPi.GPIO as GPIO   # Import GPIO library
import time               # Import time module

GPIO.setmode(GPIO.BCM)   # Use BCM pin numbering

BTN = 20                 # Button connected to GPIO 20
LED = 17                 # LED connected to GPIO 17

# Set button as input with pull-up resistor
# Default = HIGH (1), pressed = LOW (0)
GPIO.setup(BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Set LED as output
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.LOW)  # Start with LED OFF

led_state = False  # Variable to keep track of LED state

# This function runs automatically when button is pressed
def button_callback(channel):
    global led_state  # Use global variable
    
    # Toggle LED (ON → OFF or OFF → ON)
    led_state = not led_state
    
    # Set LED to new state
    GPIO.output(LED, led_state)
    
    # Print info for debugging
    print(f"Button event detected on pin {channel}")
    print(f"LED is now {'ON' if led_state else 'OFF'}")

# Detect button press (FALLING edge: 1 → 0)
# bouncetime prevents multiple triggers from one press
GPIO.add_event_detect(
    BTN,                  # Pin to monitor
    GPIO.FALLING,         # Detect button press
    callback=button_callback,  # Function to call
    bouncetime=200        # Debounce time in ms
)

try:
    print("Press the button to toggle LED (CTRL+C to stop)")
    
    while True:
        # Main loop does nothing
        # Program is waiting for interrupt events
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    GPIO.cleanup()  # Reset GPIO pins safely