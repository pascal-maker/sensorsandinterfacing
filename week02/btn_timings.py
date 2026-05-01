import RPi.GPIO as GPIO
import time
import csv
import os
import threading
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # headless-safe backend before pyplot is imported
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import gradio as gr

# --------
# config
# --------
BUTTON_PIN = 20#setting the pin number
DATA_DIR = "data"#setting the directory for the data
CSV_FILE = os.path.join(DATA_DIR, "btn_timings.csv")#setting the csv file path

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
    if state == 1:  # pin HIGH = released (pull-up resistor keeps it HIGH when not pressed)
        press_time = now
    else:  # pin LOW = pressed
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
    if not os.path.isfile(CSV_FILE):#checks if the csv file exists
        return None
    df = pd.read_csv(CSV_FILE)#reads the csv file
    if df.empty:#checks if the csv file is empty
        return None
    times = pd.to_datetime(df["Timestamp"])#converts the timestamp column to datetime objects
    durations = df["Duration (s)"]#retrieves the duration column
    fig, ax = plt.subplots(figsize=(10, 4))#creates a figure and a set of subplots
    ax.plot(times, durations, marker="o", linewidth=1, color="steelblue")#plots the data with a marker for each data point and a line connecting them
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))#formats the x axis to show hours minutes and seconds without this matplotlib would show raw datetime numbers which are unreadable
    fig.autofmt_xdate()#rotates the x-axis labels so theyt dont overlap each other
    ax.set_xlabel("Time")#timestamps when each press happened
    ax.set_ylabel("Press Duration (s)")#how long each press lasted in seconds
    ax.set_title("Button Press Durations Over Time")#sets title of the graph
    plt.tight_layout()# makes the plot look neat and tidy so the title and labels fit in the window
    plt.savefig(plot_path)#saves the plot
    plt.close()#closes the plot
    return plot_path# returns the file path of the plot

def get_session_df():#creates a pandas dataframe from the current session records
    if not records:#checks if the records list is empty
        return pd.DataFrame(columns=["Timestamp", "Duration (s)"])#returns an empty dataframe   
    return pd.DataFrame(
        [(ts.strftime("%Y-%m-%d %H:%M:%S"), round(dur, 3)) for ts, dur in records],#formats the timestamp and rounds the duration
        columns=["Timestamp", "Duration (s)"]#sets the column names
    )

def get_csv_df():#gets the csv dataframe
    if not os.path.isfile(CSV_FILE):#checks if the csv file exists
        return pd.DataFrame(columns=["Timestamp", "Duration (s)"])
    return pd.read_csv(CSV_FILE)#reads the csv file

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
    file_exists = os.path.isfile(CSV_FILE)#checks if the csv file exists
    with open(CSV_FILE, "a", newline="") as file:#opens the csv file in append mode
        writer = csv.writer(file)# creates a csv writer object
        if not file_exists:#checks if the csv file exists
            writer.writerow(["Timestamp", "Duration (s)"])#writes the header row
        for ts, duration in records:#iterates through the records list
            writer.writerow([ts.strftime("%Y-%m-%d %H:%M:%S"), round(duration, 3)])#formats the timestamp and rounds the duration
    print(f"Saved {len(records)} record(s) to {CSV_FILE}")#prints the number of records and the file path

    if records:#checks if there are any records
        build_plot()#builds the plot
        print("Plot saved.")#prints that the plot was saved

    GPIO.cleanup()#cleans up the GPIO pins    
