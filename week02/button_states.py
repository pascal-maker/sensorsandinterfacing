import RPi.GPIO as GPIO
from datetime import datetime
import csv
import os
import signal
import sys

# GPIO pin where the button is connected
BUTTON_PIN = 20

# Folder where the CSV file will be saved
DATA_DIR = "data"

# List to store all button events
# Each event will contain: timestamp, channel, state
events = []

# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Set the button pin as input with internal pull-up resistor
# Not pressed = 1
# Pressed = 0
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# This function is called automatically whenever the button changes state
def on_edge(channel):
    state = GPIO.input(channel)      # Read current button state (0 or 1)
    timestamp = datetime.now()       # Get current date and time

    # Store the event in the list
    events.append((timestamp, channel, state))

    # Print the event in a readable format
    print(f"{timestamp} | GPIO{channel} | {'PRESSED' if state == 0 else 'RELEASED'}")

# Detect both edges:
# - button press
# - button release
# callback=on_edge means the function on_edge() runs when an event happens
# bouncetime=50 helps reduce contact bounce
GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=on_edge, bouncetime=50)

# This function runs when the program is stopped with Ctrl+C
def save_and_exit(sig=None, frame=None):
    if events:
        # Create the data folder if it does not already exist
        os.makedirs(DATA_DIR, exist_ok=True)

        # Create a filename using the timestamp of the first event
        filename = events[0][0].strftime("%Y%m%d_%H%M%S") + "_button_states.csv"
        filepath = os.path.join(DATA_DIR, filename)

        # Open the CSV file and write all saved events
        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write the header row
            writer.writerow(["timestamp", "button", "state"])

            # Write each stored event
            for ts, btn, st in events:
                writer.writerow([
                    ts.strftime("%Y-%m-%d %H:%M:%S.%f"),  # formatted timestamp
                    f"GPIO{btn}",                        # button pin name
                    "PRESSED" if st == 0 else "RELEASED" # readable state
                ])

        # Show how many events were saved and where
        print(f"Saved {len(events)} events to {filepath}")

    # Reset GPIO pins before exiting
    GPIO.cleanup()

    # Stop the program
    sys.exit(0)

# When Ctrl+C is pressed, run save_and_exit()
signal.signal(signal.SIGINT, save_and_exit)

# Show startup message
print("Monitoring button states. Press Ctrl+C to stop and save data.")

# Keep the program running and waiting for button events
signal.pause()