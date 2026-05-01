"""Create a python script which will measure how long a button is pressed for
Save this data in a csv file called "btn_timings.csv" in the data folder
The csv file contains a header row, and each data row has a human readable timestamp in the format of "YYYY-MM-DD HH:MM:SS" and the duration in seconds
If you can plot this data nicely, that would be a nice addition too
 
Extra/challenge: When stopping and restarting your code, if the csv file already exists append the data (not an extra header row too!) instead of rewriting the file

"""

import RPi.GPIO as GPIO
import time
import csv
import os   
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# --------
#config
# --------



BUTTON_PIN = 20#setting the pin number
DATA_DIR = "data"#creating variable data
CSV_FILE = os.path.join(DATA_DIR, "btn_timings.csv")#creating variable csv file

GPIO.setmode(GPIO.BCM)#telling the pi to use bcm numbering system
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the pin as an input pin
os.makedirs(DATA_DIR, exist_ok=True)#setting the data directory as an output directory
#------
#state variables
#-----

press_time = None# a variable that stores when the button was pressed
records = []#list of tupple (timestamp,duration)
# -----callbacks ------
def button_event(channel):
    global press_time# declares that the function is modifying the outer press_time variable not creating a local one

    state = GPIO.input(channel)# checks the state of the button
    now = time.time()# saves current time
    if state == 1:#  button released  pin goes HIGH because of pull up resistor  save  the current time as press_time
        press_time = now #saves current time as press_time
    else:# if the button is released (pin goes LOW because of pull up resistor)
        if press_time is not None:# if there was a previous press button pressed (pin pulled LOW)
            duration = now - press_time# calculate the duration of the button press
            timestamp = datetime.now()# capture the current time as a datetime object
            records.append((timestamp,duration))# append the timestamp and duration to the records list
            print(f"{timestamp} | Duration: {duration:.3f}s")# print the timestamp and duration of the button press
            press_time = None# reset the press_time variable
#----------------
#setup event detection
#----------------
GPIO.add_event_detect(BUTTON_PIN, # pin to monitor
 GPIO.BOTH, # trigger on rising and falling edges (press and release)
  callback=button_event, # function to call when event is detected
   bouncetime=50)#you want accurate timing but a bounce too high and you will miss presses
print("Tracking button presses. Press Ctrl+C to stop.")
#----------------
#main loop
#----------------
try:
    while True:
        time.sleep(0.1)# keeps the script alive doing nothing in the GPIO callback
except KeyboardInterrupt:# catches ctrl +c
    print("Exiting...")
finally:# after ctrl +c has been pressed
    #save records
    file_exists = os.path.isfile(CSV_FILE)# checked before open the file once you open with "a" append mode the file exists regardless so you'd lose the ability to detect weather it's new and needs a header row opens the file without wiping data
    with open(CSV_FILE, "a", newline="") as file: #opens the file in append mode  "a" means append newline="" prevents blank rows between data rows in csv file
        writer = csv.writer(file)# creates a csv writer object that writes to the file 
        if not file_exists:# if not file_exists: only writes     the header on the very first run. On subsequent runs the header already exists so its skips it
            writer.writerow(["Timestamp", "Duration (s)"])# header row
        for ts,duration in records:# unpack each tuple stored by the callback ts is the datetime object duration is the float. formats the timestamp as a readable string and rounds duration to 3 decimal places before writing.
            writer.writerow([ts.strftime("%Y-%m-%d %H:%M:%S"),round(duration,3)])# this takes the timestamp and formats it as a string and rounds the duration to 3 decimal places and writes it to the csv file
        print(f"Saved data to {CSV_FILE}")# prints that the data has been saved to the csv file
    #----------------
    #plot the data as the same as the CSV
    #----------------
    if len(records) > 0:#if the records list is not empty only run this if the records list is empty no graph is made
        times = []#empty list to store the timestamp
        durations = []#empty list to store the duration
        for r in records:# list of datetime objects each record is a tuple (timestamp,duration)
            times.append(r[0])# timestamp (index 0) is added to the times list
            durations.append(r[1])# duration (index 1) is added to the durations list
        fig, ax = plt.subplots(figsize=(10,4))#creates a figure and a set of subplots
        ax.plot(times, durations, marker = 'o')# put a dot at each point so individual presses are visible.
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))#format the x axis to show hours minutes and seconds without this matplotlib would show raw datetime numbers which are unreadable
        fig.autofmt_xdate()#rotates the x-axis labels so theyt dont overlap each other
        ax.set_xlabel("Time")#timestamps when each press happened
        ax.set_ylabel("Press Duration (s)")#how long each press lasted in seconds
        ax.set_title("Button Press Durations Over Time")#sets title of the graph
        plt.tight_layout()# makes the plot look neat and tidy so the title and labels fit in the window
        plt.savefig(os.path.join(DATA_DIR, "btn_timings.png"))# builds the file path proply for the graph and saves it to the data folder in a .png format (with the .png extension it automatically formats it as a png file) than hardcoding the string showing how csv is defined
        plt.close()#closes the plot
        print("Plot saved")# prints that the plot has been saved
GPIO.cleanup()#resets the GPIO pins
