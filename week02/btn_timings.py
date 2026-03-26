import RPi.GPIO as GPIO
import os
import time
import csv
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BUTTON = 20
CSV_FILE = "data/btn_timings.csv" # this is the f  ile where the data will be stored
PLOT_FILE = "data/button_press_durations.png"

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#make a data folder if t does not exists
os.makedirs("data", exist_ok=True)

#make a ybuqye fukneae
file_exists = os.path.exists(CSV_FILE)
press_start_time = None
previous_state = GPIO.input(BUTTON)
print("Button timing logger started.")
print("Press the button to record a press.")
print("Press Ctrl+C to exit.")

try:
    with open(CSV_FILE , 'a',newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "DurationSeconds"])# this is the header of the csv file
            
        while True:
            current_state = GPIO.input(BUTTON)
            if previous_state == GPIO.HIGH and current_state == GPIO.LOW:#if the button is not pressed and now pressed
                press_start_time = time.time()#record the time when the button is pressed
                print("Button pressed")
                time.sleep(0.02)
            elif previous_state == GPIO.LOW and current_state == GPIO.HIGH:#if the button is pressed and now not pressed
                if press_start_time is not None:
                    press_end_time = time.time()#record the time when the button is not pressed
                    duration = round(press_end_time - press_start_time, 3)#calculate the duration of the button press
                    human_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")#format the time to a human readable format
                    writer.writerow([human_timestamp, duration])#write the time and duration to the csv file
                    file.flush()
                    print(f"{human_timestamp} - duration: {duration} seconds")#print the time and duration to the console
                    press_start_time = None#reset the press start time
                    time.sleep(0.02)
            previous_state = current_state
            time.sleep(0.005)
                

                
                

except KeyboardInterrupt:
    print("\nButton press logger stopped.")
finally:
    GPIO.cleanup()
                
 #plot all saved atata
timestamps  = []    
durations = []

if os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0:#check if the file exists and has data
    with open(CSV_FILE, 'r') as file:
        reader = csv.reader(file)#create a csv reader object
        next(reader) # Skip header
        for row in reader:
            timestamps.append(datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f"))#convert the timestamp to a datetime object
            durations.append(float(row[1]))#convert the duration to a float
            
if timestamps:
    fig,ax  = plt.subplots(figsize=(12,6))
    ax.plot_date(timestamps, durations, linestyle="-", marker="o", markersize=4, color="b", alpha=0.7)#plot the data
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))#format the x-axis to display the date and time
    fig.autofmt_xdate()
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("Duration (seconds)")
    ax.set_title("Button Press Durations")
    ax.legend()
    plt.tight_layout()
    plt.savefig("data/button_press_durations.png")
    print("Plot saved to data/button_press_durations.png")
    plt.close()
    print(f" Plot saved to {PLOT_FILE}")
else:
    print("No data to plot.")
