from RPi import GPIO
import time
from datetime import datetime
import csv
import os



# the GPIO pin number we connected the button to
btn = 20
# A list to store all the logged rows
data = []#this is where all the data will be stored before it is saved to the csv file

GPIO.setmode(GPIO.BCM)
GPIO.setup(btn,GPIO.IN,pull_up_down=GPIO.PUD_UP)
press_time = None# this is used to store the time when the button is pressed  so we use it to none to store initial values 

def button_callback(channel):#this is the callback function that is called when the button is pressed 
    global press_time#we need to make this global so that we can access it from outside the function
    state = GPIO.input(channel)# reads the state of the button

    if state == GPIO.LOW: # if the state is low the button is pressed
        press_time = datetime.now()# stores the time when the button is pressed
        print("Pressed")

    else:
        if press_time is not None:# this makes sure that the button was pressed before we try to calculate the duration
            duration = (datetime.now() - press_time).total_seconds()#calculates the duration of the button press
            print(f"Released after {duration:.3f} seconds")
            data.append({
                "time": press_time.strftime("%Y-%m-%d %H:%M:%S"),#formats the time to a string
                "duration": duration
            })
            press_time = None# reset so a stray second release event doesn't log a bogus duration


GPIO.add_event_detect(btn, GPIO.BOTH, callback=button_callback, bouncetime=200)#tells the pi to watch for changes on the button when the button is pressed or released

try:
    while True:
        print("Running main program")#this line will print every 5 seconds
        time.sleep(5)
except KeyboardInterrupt:#this will catch the keyboard interrupt and save the data
    print("Saving data")

    os.makedirs("data", exist_ok=True)#this will create a directory called data if it does not exist
    filename = datetime.now().strftime("data/%Y-%m-%d_%H-%M-%S_button.csv")#this will create a filename with the current date and time (dashes not colons - colons are invalid in filenames)
    
    with open(filename, "w", newline="") as f:#opens the file in write mode
        writer = csv.DictWriter(f, fieldnames=["time", "duration"])#this creates a csv writer object
        writer.writeheader()#this writes the header row to the csv file
        writer.writerows(data)#this writes the data to the csv file
    GPIO.cleanup()#this cleans up the GPIO pins