import RPi.GPIO as GPIO
from datetime import datetime
import csv
import os
import signal
import sys

BUTTON_PIN = 20
DATA_DIR = "data"
EVENTS = []
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def on_edge(channel):
    state = GPIO.input(BUTTON_PIN)
    timestamp = datetime.now
    EVENTS.append((timestamp, state))
    print(f"{timestamp} | GPIO{channel} | {'PRESSED' if state == 0 else 'RELEASED'}")
    
GPIO.add_event_detect(BUTTON_PIN, GPIO.BOTH, callback=on_edge, bouncetime=50)


def save_and_exit(sig=None,frame=None):
    if events:
        os.makedirs(DATA_DIR, exist_ok=True)
        filename = events[0][0].strftime("%Y%m%d_%H%M%S") + "_button_states.csv"
        filepath = os.path.join(DATA_DIR, filename)

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "button", "state"])
            for ts, btn, st in events:
                writer.writerow([
                    ts.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    f"GPIO{btn}",
                    "PRESSED" if st == 0 else "RELEASED"
                ])

        print(f"\nSaved {len(events)} events to {filepath}")

    GPIO.cleanup()
    sys.exit(0)

signal.signal(signal.SIGINT, save_and_exit)

print(f"Tracking button on GPIO{BUTTON_PIN}. Press Ctrl+C to stop and save.")
signal.pause()

