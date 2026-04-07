#import the libraries

import os
import csv
import time
from datetime import datetime 
from RPi import GPIO
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#
GPIO.setmode(GPIO.BCM) #set the mode of the GPIO pins to BCM
BUTTON = 20 #define the button pins
POLL_DELAY = 0.01#delay between polls
DATA_DIR = "data"#data directory
CSV_FILE = os.path.join(DATA_DIR, "btn_timings.csv")#create csv filename
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)#set the button pin as input with pull up resistor

os.makedirs(DATA_DIR, exist_ok=True)#create data directory if it doesn't exist

#storage lists && variables
timestamps = []#list to store timestamps
durations = []#list to store durations
prev_state = GPIO.input(BUTTON)#previous state of the button
press_start_time = None#start time of the button press

print("Program started. Press Ctrl+C to stop")#print message
print("Tracking duration")#print message

try:
    while True:
        current_state = GPIO.input(BUTTON)#current state of the button
        if current_state == GPIO.LOW and prev_state == GPIO.HIGH:#if the button is pressed
            press_start_time = time.time()#start time of the button press
            print("Button pressed")#print message
        elif current_state == GPIO.HIGH and prev_state == GPIO.LOW:#if the button is released
           if press_start_time is not None:#if the button was pressed
            duration = time.time() - press_start_time#calculate the duration of the button press
            now = datetime.now()#get the current time
            timestamps.append(now)#append the timestamp
            durations.append(duration)#append the duration
            print(f"{now.strftime('%Y-%m-%d %H:%M:%S.%f')} GPIO {BUTTON} released")#print the timestamp and duration
            press_start_time = None#reset the start time

        prev_state = current_state#update the previous state
        time.sleep(POLL_DELAY)#delay between polls
            
            

except KeyboardInterrupt:#when the user press ctrl+c
    print("Exiting program")
finally:
    file_exists = os.path.exists(CSV_FILE)#check if the file exists
    mode = "a" if file_exists else "w"#set the mode to append or write

    with open(CSV_FILE, mode, newline='') as csvfile:#open the csv file
        writer = csv.writer(csvfile)#create a csv writer
        if not file_exists:#if the file doesn't exist
            writer.writerow(["Timestamp", "Duration"])#write the header
        for ts, duration in zip(timestamps, durations):#loop through the timestamps and durations
            writer.writerow([ts.strftime('%Y-%m-%d %H:%M:%S.%f'), duration])#write the timestamp and duration
    print(f"Data saved to {CSV_FILE}")#print the filename

  

    #make plot

    if len(timestamps) > 0:#if there are timestamps
        fig,ax = plt.subplots(figsize=(8,4))#create figure and axes
        ax.plot(timestamps, button_states, marker='o', linestyle='-')#plot the data
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))#set the major formatter
        fig.autofmt_xdate()#auto format the x date
        ax.set_xlabel("Time")#set the x label
        ax.set_ylabel("Duration")#set the y label
        ax.set_title("Button Press Duration")#set the title
        ax.legend()#
        plt.tight_layout()
        
        plot_filename = os.path.join(DATA_DIR, f"btn_timings.png")#create plot filename
        plt.savefig(plot_filename)#save the plot
        plt.close()
        print(f"Plot saved to {plot_filename}")     #print the plot filename
    else:
        print("No  button changes detected,so no plot generated")#print the message
    GPIO.cleanup()
        
        

    
    