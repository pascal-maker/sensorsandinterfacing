"""Record two buttons' press/release events and plot their states."""

from datetime import datetime
from pathlib import Path
import time

from RPi import GPIO#the RPi.GPIO library is used to control the GPIO pins on a Raspberry Pi

from csv_plotting import CSVStorage, TimeSeriesPlotter


BUTTONS = {
    20: "BUTTON_1",
    21: "BUTTON_2",
}

DATA_DIR = Path(__file__).resolve().parent / "data"#creates the data directory
events = []#list to store the events
state_plotter = TimeSeriesPlotter(
    "Button State Changes Over Time",
    y_label="Button state",
)


def button_changed(channel):#callback function that is called when a button is pressed or released
    """Store an event whenever a button is pressed or released."""
    timestamp = datetime.now()#gets the current date and time
    state = GPIO.input(channel)#gets the current state of the button
    button_name = BUTTONS[channel]#gets the name of the button
    state_name = "PRESSED" if state == GPIO.LOW else "RELEASED"#checks if the button is pressed or released

    events.append((timestamp, button_name, state))#appends the event to the list
    print(f"{timestamp:%Y-%m-%d %H:%M:%S.%f} | {button_name} | {state_name}")#prints the event


def save_csv(csv_path):#saves the events to a csv file
    """Save all recorded events to a CSV file."""
    storage = CSVStorage(csv_path, ["Timestamp", "Button", "State"])
    storage.overwrite(
        [
            [
                timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),#formats the date and time to a string
                button_name,
                "PRESSED" if state == GPIO.LOW else "RELEASED",#checks if the button is pressed or released
            ]
            for timestamp, button_name, state in events
        ]
    )

    print(f"Saved {len(events)} event(s) to {csv_path}")#prints that the data has been saved to the csv file


def save_plot(image_path):#saves the events to a png file
    """Plot the recorded HIGH/LOW button states when events exist."""
    if not events:
        print("No events recorded, so no plot was created.")#prints that no events were recorded
        return

    # Every event is a tuple containing:
    #     (timestamp, button_name, state)
    #
    # Python indexes start at 0, so event[0] is the timestamp and event[2]
    # is the GPIO state. These list comprehensions extract those values from
    # every event to create the x-axis and y-axis data for the graph.
    #
    # The first line is a shorter version of:
    #     times = []
    #     for event in events:
    #         times.append(event[0])
    times = [event[0] for event in events]#extract timestamps
    states = [event[2] for event in events]#extract states from events

    state_plotter.save(
        image_path,
        times,
        states,
        style="step",
        y_ticks=([GPIO.LOW, GPIO.HIGH], ["Pressed", "Released"]),
    )

    print(f"Saved plot to {image_path}")#prints that the data has been saved to the image file


def main():
    GPIO.setmode(GPIO.BCM)#set the GPIO mode

    # Pull-ups make an unpressed button HIGH and a pressed button LOW.
    for pin in BUTTONS:#iterates through the buttons
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)#sets up the pins
        GPIO.add_event_detect(# detects the changes in the button states
            pin,#the pin number to detect changes on
            GPIO.BOTH,#detects both rising and falling edges
            callback=button_changed,#calls the button_changed function when a button is pressed or released
            bouncetime=200,#bouncetime is used to prevent multiple events from being triggered by a single press or release
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)#creates the data directory

    print("Tracking button state changes. Press Ctrl+C to save and exit.")

    try:
        while True:#keeps the program running until the user presses ctrl+c 
            time.sleep(0.5)#pauses the program for 0.5 seconds
    except KeyboardInterrupt:
        print("\nCtrl+C received. Saving results...")#prints that the program has been stopped
    finally:
        # One timestamp keeps the CSV and PNG filenames paired.
        filename_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")#formats the date and time to a string
        csv_path = DATA_DIR / f"{filename_time}_button_states.csv"#creates the csv file path
        image_path = DATA_DIR / f"{filename_time}_button_states.png"#creates the image file path

        try:
            save_csv(csv_path)#saves the csv file
            save_plot(image_path)#saves the plot
        finally:
            GPIO.cleanup()#cleans up the GPIO pins
            print("GPIO cleanup complete.")#prints that the program has been stopped


if __name__ == "__main__":
    main()
