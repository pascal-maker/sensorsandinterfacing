import RPi.GPIO as GPIO
from datetime import datetime
import csv
import os
import signal
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# GPIO pin where the button is connected
BUTTON_PIN = 20

# Folder where data and plot will be stored
DATA_DIR = "data"

# CSV file where all button timings will be appended
CSV_FILE = os.path.join(DATA_DIR, "btn_timings.csv")

# Stores the moment when the button was pressed
press_time = None

# List to store all measured press durations
# Each item will contain: (press timestamp, duration in seconds)
timings = []

# Use BCM GPIO numbering
GPIO.setmode(GPIO.BCM)

# Set button pin as input with internal pull-up resistor
# Not pressed = 1
# Pressed = 0
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# This function runs automatically every time the button changes state
def on_edge(channel):
    global press_time  # We want to update the global press_time variable

    state = GPIO.input(channel)  # Read current button state

    if state == 0:  # Button is pressed
        press_time = datetime.now()  # Save the exact press time
        print(f"Pressed at {press_time.strftime('%H:%M:%S')}")

    else:  # Button is released
        if press_time is not None:  # Only calculate duration if a press was recorded
            duration = (datetime.now() - press_time).total_seconds()  # Time held down
            timings.append((press_time, duration))  # Store timestamp + duration
            print(f"Released | duration: {duration:.3f}s")
            press_time = None  # Reset press_time for next press

# Detect both button press and release
# callback=on_edge means the function runs automatically on each edge
# bouncetime=50 helps reduce contact bounce
GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=on_edge, bouncetime=50)

# This function reads the CSV file and makes a graph of button press durations
def plot():
    times = []       # List for timestamps
    durations = []   # List for durations

    # Open the CSV file and read all saved rows
    with open(CSV_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            times.append(datetime.strptime(row["timestamp"], "%Y-%m-%d %H:%M:%S"))
            durations.append(float(row["duration_seconds"]))

    # Create the plot
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(times, durations, marker="o", linestyle="-", label="Duration (s)")

    # Format the x-axis to show only time
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
    fig.autofmt_xdate()

    # Add labels and title
    ax.set_xlabel("Time")
    ax.set_ylabel("Duration (seconds)")
    ax.set_title("Button Press Durations")
    ax.legend()

    # Save plot to PNG file
    plt.tight_layout()
    plt.savefig(os.path.join(DATA_DIR, "button_timing.png"))
    plt.close()

    print("Plot saved to data/button_timing.png")

# This function runs when Ctrl+C is pressed
def save_and_exit(sig=None, frame=None):
    if timings:
        # Create the data directory if it does not exist
        os.makedirs(DATA_DIR, exist_ok=True)

        # Check if CSV file already exists
        file_exists = os.path.isfile(CSV_FILE)

        # Open CSV in append mode so old data is kept
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)

            # Write header only if file does not exist yet
            if not file_exists:
                writer.writerow(["timestamp", "duration_seconds"])

            # Write each timing entry
            for ts, dur in timings:
                writer.writerow([
                    ts.strftime("%Y-%m-%d %H:%M:%S"),
                    f"{dur:.3f}"
                ])

        print(f"\nAppended {len(timings)} entries to {CSV_FILE}")

        # Create plot after saving CSV
        plot()

    # Reset GPIO pins before exiting
    GPIO.cleanup()

    # Stop the program
    sys.exit(0)

# When Ctrl+C is pressed, run save_and_exit()
signal.signal(signal.SIGINT, save_and_exit)

# Show startup message
print(f"Tracking button hold duration on GPIO{BUTTON_PIN}. Press Ctrl+C to stop and save.")

# Keep the program running and waiting for button events
signal.pause()