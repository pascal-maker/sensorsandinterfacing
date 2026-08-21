import RPi.GPIO as GPIO#import
import time#import time library
import csv#import csv library
import os#import os library
from datetime import datetime#import datetime library
import matplotlib.pyplot as plt#import matplotlib library
import matplotlib.dates as mdates#import matplotlib dates library
BUTTON_1 = 20#setting up the first button
BUTTON_2 = 21#setting up the second button
buttons = {BUTTON_1:"BUTTON_1", BUTTON_2:"BUTTON_2"} #creates a dictionary to map button pins to names makes them human readable in the CSV and plot , we need the dictionary for the callback function to look up the name associated with the pin number when the button is pressed or released a dictionary lets you do buttons[channel] inside the calback instantly get a readable name from the pin number. the gpiocallabck gives you a pin number (channel_ an an index so dictionary natural lookup structure 
GPIO.setmode(GPIO.BCM)#setting up the GPIO mode
for button in buttons:#run once for each button in the list
    GPIO.setup(button,GPIO.IN,pull_up_down=GPIO.PUD_UP)#setting up the buttons as inputs with pull up resistors

events = []#create an empty list called events to store the button presses/releases appended here as a tuple (timestamp,button_name,state )

os.makedirs("data",exist_ok=True)#create a directory called data if it does not exist to save logged events exist-ok=True means it wont crash if the folder already exists

#callback function
# runs whenever button state changes
def button_changed(channel):#this function will run whenever a button is pressed or released a callback function you dont call it yourself gpio.calls it automatically whenver a button state changes states it automically whenver a button changes state it records the current time 
    timestamp = datetime.now()#sets the timestamp to the current time records the current time
    state = GPIO.input(channel)#sets the state to the current state of the button reads whether the pin is high (1) or low (0)
    button_name = buttons[channel]#sets the button name to the current button looks up human-readable name from the button list  dict using the pin number 
    events.append((timestamp, button_name, state))#adds the timestamp, button name and state to the events list append all three as a tuple to events
    print(f"{timestamp} - {button_name} changed state to {state}")#prints the timestamp, button name and state outputs the data to the terminal

#add edge detection
for pin in buttons:#run once for each button in the list register the save callback on ever pin the buttons dict ,so buttons share one handler te channel paramreter inside callback tells you which button changed so it can distinguish between events from different pins registers the same callback on evry pin in the buttons dict, so all buttons share one handler. the channel parameter inside the callback tells you which pin is fired.
    GPIO.add_event_detect(pin, GPIO.BOTH, callback=button_changed, bouncetime=200)#detects edge detection on the button means the callback fires on both edges rising and falling button pressed and released not just one direction  bouncetime is the time in milliseconds to wait before detecting another edge so ignore noisy/multiple triggers from a single physical press
#gpio.both means that the callback function will be called when the button is pressed or released GPIO.RISING only when the button is pressed GPIO.FALLING only when the button is released
print("Tracking button state changes.")#prints that button state changes are being tracked
print("Press Ctrl+C to save and exit.")#prints that the user should press Ctrl+C to save and exit
try:
    while True:#runs until the user presses Ctrl+C
        time.sleep(0.5)#waits for 0.5 seconds
except KeyboardInterrupt:#runs when the user presses Ctrl+C
    print("Exiting...")#prints that the program is exiting
finally:#runs after the user presses Ctrl+C
    filename_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")#sets the filename time to the current time creates timestamp string like 2026-05-01_14-30-22 used in both output files so each run produces uniquely named files and old data isnt overwritten.
    csv_file = f"data/{filename_time}_button_states.csv"#sets the csv file name to the current time f string means it will substiute
    image_file = f"data/{filename_time}_button_states.png"#sets the image file name to the current time    substitutes this variable into the string so that the image file name is different every time the program is run this ensures that the previous image file is not overwritten and a new image file is created every time the program is run

    #Save csv

    with open(csv_file, "w", newline="") as file:#open the csv file in write mode
        writer = csv.writer(file)#create a csv writer
        writer.writerow(["Timestamp", "Button", "State"])#writes the header row

        for row in events:#run once for each row in the events list
            writer.writerow([row[0].strftime("%Y-%m-%d %H:%M:%S.%f"), row[1], row[2]])#writes the events to the csv file in the correct format

    #save data to csv
    print(f"Saved data to {csv_file}")#prints that the data has been saved to the csv file

    #make graph
    if len(events) > 0:# if the events list is not empty only run events is not empty no graph is made
        times = [row[0] for row in events]#extracts the timestamps from the events list
        states = [row[2] for row in events]#extracts the states from the events list

        #create figure and axis
        fig, ax = plt.subplots(figsize=(10, 4))#creates a figure and axis

        #plot button states as a step plot
        ax.plot(times, states, marker='o',linestyle='-')#plots the button states as a step plot
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))#sets the x-axis date formatter formats the x-axis date as HH:MM:SS instead of raw datime objects
        fig.autofmt_xdate()#auto formats the x-axis date tilts the x-axis labels do they dont overlap

        ax.set_xlabel("Time")#sets the x-axis label
        ax.set_ylabel("Button State")#sets the y-axis label
        ax.set_title("Button State Changes Over Time")#sets the title of the graph
        ax.set_yticks([0,1])#sets the y-axis ticks makes them 0 and 1 no other values allowed on the y-axis so it only shows up and down states 0 or 1 
        plt.tight_layout()#adjusts the plot to prevent labels from overlapping
        plt.savefig(image_file)#saves the figure 
        plt.close()#closes the figure to save memory
        print(f"Saved data to {image_file}")#prints that the data has been saved to the image file
    GPIO.cleanup()#resets the GPIO pins
    print("GPIO cleanup completed")#prints that the GPIO pins have been reset all gpio pins back to their default input state. without this pin can stay in their last configured mode, which can cause issues or unexepected behavior the next time the script runs.