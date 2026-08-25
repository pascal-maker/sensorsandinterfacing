import RPi.GPIO as GPIO
import time
import os
import threading
from datetime import datetime
import pandas as pd
import gradio as gr

from csv_plotting import CSVStorage, TimeSeriesPlotter

# --------
# config
# --------
BUTTON_PIN = 20#setting the pin number
BASE_DIR = os.path.dirname(os.path.abspath(__file__))#folder containing this script
DATA_DIR = os.path.join(BASE_DIR, "data")#always use Week 2's data folder
CSV_FILE = os.path.join(DATA_DIR, "btn_timings.csv")#setting the csv file path
CSV_HEADERS = ["Timestamp", "Duration (s)"]
csv_storage = CSVStorage(CSV_FILE, CSV_HEADERS)
plotter = TimeSeriesPlotter(
    "Button Press Durations Over Time",
    y_label="Press Duration (s)",
)

GPIO.setmode(GPIO.BCM)#setting the mode to bcm
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the pin as an input with pull up resistor
os.makedirs(DATA_DIR, exist_ok=True)#setting the data directory as an output directory

# ------
# state variables
# -----
press_time = None# declaring press time
records = []  # list of (datetime, float) tuples

# ----- callbacks ------
def button_event(channel):# declares the button event function
    global press_time# declares the function is modifying the outer press_time variable not creating a local one
    state = GPIO.input(channel)# checks the state of the button
    now = time.time()# saves current time

    # The pull-up makes the button active-LOW:
    # LOW means pressed, so start the timer on the falling edge.
    if state == GPIO.LOW:
        press_time = now

    # HIGH means released, so stop the timer on the rising edge.
    elif state == GPIO.HIGH:
        if press_time is not None:# if the button was previously pressed
            duration = now - press_time# calculate the duration of the button press
            timestamp = datetime.now()# save the current time
            records.append((timestamp, duration))# appends the timestamp and duration to the records list
            print(f"{timestamp} | Duration: {duration:.3f}s")# prints the timestamp and duration of the button press
            press_time = None# resets the press_time variable

GPIO.add_event_detect(
    BUTTON_PIN,# pin to monitor
    GPIO.BOTH,# trigger on rising and falling edges (press and release)
    callback=button_event,# function to call when event is detected
    bouncetime=50# you want accurate timing but a bounce too high and you will miss presses
)

# ----------------
# helpers
# ----------------
def build_plot():
    """Regenerate plot from current CSV data and return the saved path."""
    plot_path = os.path.join(DATA_DIR, "btn_timings.png")#build the file path proply for the graph and saves it to the data folder in a .png format (with the .png extension it automatically formats it as a png file) than hardcoding the string showing how csv is defined
    rows = csv_storage.read_rows()
    if not rows:
        return None
    times = pd.to_datetime([row["Timestamp"] for row in rows])
    durations = [float(row["Duration (s)"]) for row in rows]
    return plotter.save(plot_path, times, durations)

def get_session_df():#creates a pandas dataframe from the current session records
    if not records:#checks if the records list is empty
        return pd.DataFrame(columns=CSV_HEADERS)#returns an empty dataframe
    return pd.DataFrame(
        [(ts.strftime("%Y-%m-%d %H:%M:%S"), round(dur, 3)) for ts, dur in records],#formats the timestamp and rounds the duration
        columns=["Timestamp", "Duration (s)"]#sets the column names
    )

def get_csv_df():#gets the csv dataframe
    return csv_storage.to_dataframe()

# ----------------
# Gradio UI
# ----------------
with gr.Blocks(title="Button Timing Monitor") as demo:#
    gr.Markdown("# Button Press Timing Monitor")#
    gr.Markdown("Live dashboard — data is appended to CSV on Ctrl+C.")#

    with gr.Row():# creates two columns side by side
        with gr.Column():# first column
            gr.Markdown("### This Session")#
            session_table = gr.DataFrame(value=get_session_df, every=2)#
        with gr.Column():# second column
            gr.Markdown("### All Saved Data (CSV)")#
            csv_table = gr.DataFrame(value=get_csv_df, every=5)#

    plot_img = gr.Image(value=build_plot, every=5, label="Press Duration Plot")#plots the graph


def _run_gradio():
    demo.launch(server_name="0.0.0.0", server_port=7861, quiet=True, prevent_thread_lock=True)#starts the gradio server


threading.Thread(target=_run_gradio, daemon=True).start()#starts the gradio server in a separate thread so it doesnt block the main thread
print("Gradio dashboard: http://<pi-ip>:7861")#prints the url for the gradio dashboard
print("Tracking button presses. Press Ctrl+C to stop.")#prints a message to the console indicating that the program is tracking button presses and how to stop it

# ----------------
# main loop
# ----------------
try:
    while True:# loops continuously to keep the program running
        time.sleep(0.1)# pauses the program for 0.1 seconds to reduce cpu usage
except KeyboardInterrupt:# if keyboard interrupt is received
    print("\nExiting...")# prints exit message
finally:# append this session to CSV
    rows = [
        [ts.strftime("%Y-%m-%d %H:%M:%S"), round(duration, 3)]
        for ts, duration in records
    ]
    csv_storage.append(rows)
    print(f"Saved {len(records)} record(s) to {CSV_FILE}")#prints the number of records and the file path

    if records:#checks if there are any records
        build_plot()#builds the plot
        print("Plot saved.")#prints that the plot was saved

    GPIO.cleanup()#cleans up the GPIO pins    
