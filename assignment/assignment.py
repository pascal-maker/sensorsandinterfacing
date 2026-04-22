import time#used to add delays
import threading#used to run the screens in different threads
import RPi.GPIO as GPIO#used to control the GPIO pins
import screen1#import the first screen
import screen2#import the second screen
import screen3#import the third screen
import screen4#import the fourth screen
import screen5#import the fifth screen
import screen6#import the sixth screen
JOY_BUTTON = 7#joystick button pin
screens = [
    screen1.run,
    screen2.run,
    screen3.run,
    screen4.run,
    screen5.run,
    screen6.run,

]
current_screen = 0#current screen index
press_count = 0#number of times the joystick has been pressed
screen_thread = None#thread that runs the current screen
stop_event = None#event to stop the current screen

switch_lock = threading.Lock()#lock to prevent race conditions when switching screens

def start_screen(index):#start the screen at the given index
    global screen_thread, stop_event#declare the global variables
    stop_event = threading.Event()#create a stop event
    screen_thread = threading.Thread(target=screens[index], args=(stop_event,),daemon=True)#create a thread for the screen
    screen_thread.start()#start the thread
    print(f"Started screen {index + 1}")
    

def switch_to_next_screen():#switch to the next screen
   global current_screen,screen_thread,stop_event#declare the global variables
   with switch_lock:#lock to prevent race conditions when switching screens
    if stop_event is not None:#check if the stop event is set
        stop_event.set()

    if screen_thread is not None:#check if the screen thread is not None
        screen_thread.join(timeout=0.5)#wait for the screen thread to finish
        current_screen = (current_screen + 1) % len(screens)#increment the screen index
        start_screen(current_screen)    #start the next screen
   

def joystick_pressed(channel):#callback function for the joystick button
    global press_count#declare the global variable
    press_count += 1#increment the press count
    print(f"Joystick pressed {press_count} times")
    switch_to_next_screen()

def main():
    global stop_event,screen_thread
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(JOY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(JOY_BUTTON, GPIO.FALLING, callback=joystick_pressed, bouncetime=200)
    start_screen(current_screen)#start the first screen
    try:
        while True:
            time.sleep(1)#wait a tiny bit
    except KeyboardInterrupt:#catch the keyboard interrupt
        print("Exiting")
    finally:#finally block to clean up
        if stop_event is not None:#check if the stop event is set
            stop_event.set()
        if screen_thread is not None and screen_thread.is_alive():#check if the screen thread is not None and is alive
            screen_thread.join(timeout=0.5)#wait for the screen thread to finish
        GPIO.cleanup()#clean up the GPIO pins
        

if __name__ == "__main__":
    main()#run the main function


    
    