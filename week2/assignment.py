import os
import csv
import time
from datetime import datetime 
from RPi import GPIO
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

GPIO.setmode(GPIO.BCM) #set the mode of the GPIO pins to BCM
BUTTON = 20 #define the button pins
POLL_DELAY = 0.01#delay between polls
DATA_DIR = "data"#data directory
CSV_FILE = os.path.join(DATA_DIR, "btn_timings.csv")
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)

os.makedirs(DATA_DIR, exist_ok=True)

#storage lists
timestamps = []#list to store timestamps
durations = []#list to store durations
prev_state = GPIO.input(BUTTON)
press_start_time = None

print("Program started. Press Ctrl+C to stop")
print("Tracking duration")

try:
    while True:
        current_state = GPIO.input(BUTTON)
        if current_state == GPIO.LOW and prev_state == GPIO.HIGH:
            press_start_time = time.time()
            print("Button pressed")
        elif current_state == GPIO.HIGH and prev_state == GPIO.LOW:
           if press_start_time is not None:
            duration = time.time() - press_start_time
            now = datetime.now()
            timestamps.append(now)
            durations.append(duration)
            print(f"{now.strftime('%Y-%m-%d %H:%M:%S.%f')} GPIO {BUTTON} released")
            press_start_time = None

        prev_state = current_state
        time.sleep(POLL_DELAY)
            
            

except KeyboardInterrupt:#when the user press ctrl+c
    print("Exiting program")
finally:
    file_exists = os.path.exists(CSV_FILE)
    mode = "a" if file_exists else "w"

    with open(CSV_FILE, mode, newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["Timestamp", "Duration"])
        for ts, duration in zip(timestamps, durations):
            writer.writerow([ts.strftime('%Y-%m-%d %H:%M:%S.%f'), duration])
    print(f"Data saved to {CSV_FILE}")

  

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
        
        

    
    