import os
import csv
import time
from datetime import datetime 
from RPi import GPIO
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

GPIO.setmode(GPIO.BCM) #set the mode of the GPIO pins to BCM
BUTTON_PINS = [20,21]#define the button pins
GPIO.setup(BUTTON_PINS, GPIO.IN, pull_up_down=GPIO.PUD_UP)
POLL_DELAY = 0.01#delay between polls
DATA_DIR = "data"#data directory

#storage lists
timestamps = []#list to store timestamps
button_states = []#list to store button states
button_names = []#list to store button names

#keeptrack of previous states
prev_states = {}#dictionary to store previous states

#setup button pins
for pin in BUTTON_PINS:#loop through the button pins
    prev_states[pin] = GPIO.input(pin)#set the previous state of the button

#create data folder if neede
os.makedirs(DATA_DIR, exist_ok=True)#create data folder if needed
print("Program started. Press Ctrl+C to stop")
print("Tracking button state changes")



#main loop
try:
    while True:
        for pin in BUTTON_PINS:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)#loop through the button pins
            current_state = GPIO.input(pin)#current state of the button
            if current_state != prev_states[pin]:#if current state is different from previous state
                now = datetime.now()#current time
                timestamps.append(now)#append current time to timestamps list
                button_states.append(current_state)#append current state to button states list
                button_names.append(f"GPIO {pin}")#append button name to button names list

                if current_state == GPIO.LOW:#if button is pressed
                    print(f"{now.strftime('%Y-%m-%d %H:%M:%S.%f')} GPIO {pin} pressed")
                else:#if button is released
                    print(f"{now.strftime('%Y-%m-%d %H:%M:%S.%f')} GPIO {pin} released")
                prev_states[pin] = current_state
        time.sleep(POLL_DELAY)#wait for poll delay
except KeyboardInterrupt:#when the user press ctrl+c
    print("Exiting program")
finally:
    filename_prefix = time.strftime("%Y%m%d_%H%M%S")#create filename prefix
    csv_filename = os.path.join(DATA_DIR, f"buttons_data_{filename_prefix}.csv")#create csv filename

    with open(csv_filename, 'w', newline='') as csvfile:#open csv file
        writer = csv.writer(csvfile)#create csv writer
        writer.writerow(["Timestamp", "Button", "State"])#write header
        
        for ts ,btn, state in zip(timestamps, button_names, button_states):#loop through the timestamps,button names and button states
            state_str = "pressed" if state == GPIO.LOW else "released"#convert state to string
            writer.writerow([ts.strftime('%Y-%m-%d %H:%M:%S.%f'), btn, state_str])#write the data to the csv file
    print(f"Data saved to {csv_filename}")#print the csv filename

    #make plot

    if len(timestamps) > 0:#if there are timestamps
        fig,ax = plt.subplots(figsize=(8,4))#create figure and axes
        ax.plot(timestamps, button_states, marker='o', linestyle='-')#plot the data
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))#set the major formatter
        fig.autofmt_xdate()#auto format the x date
        ax.set_xlabel("Time")#set the x label
        ax.set_ylabel("Button State")#set the y label
        ax.set_title("Realtime Button State")#set the title
        ax.legend()#
        plt.tight_layout()
        
        plot_filename = os.path.join(DATA_DIR, f"button_plot_{filename_prefix}.png")#create plot filename
        plt.savefig(plot_filename)#save the plot
        plt.close()
        print(f"Plot saved to {plot_filename}")     #print the plot filename
    else:
        print("No  button changes detetecd,so no plot generated")#print the message
    GPIO.cleanup()
        
        

    
    