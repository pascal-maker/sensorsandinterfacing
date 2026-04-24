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
    screen1.run,#list of screens to run
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

    screen_thread = threading.Thread(#create a thread for the screen
        target=screens[index],#target is the screen to run
        args=(stop_event,),#arguments to pass to the screen
        daemon=True#set as a daemon thread so it will close when the main thread closes
    )

    screen_thread.start()#start the thread
    print(f"Started screen {index + 1}")#print the screen number


def switch_to_next_screen():#switch to the next screen
    global current_screen, screen_thread, stop_event#declare the global variables

    with switch_lock:
        if stop_event is not None:#stop the current screen if it is running
            stop_event.set()

        if screen_thread is not None and screen_thread.is_alive():#wait for the current screen to finish
            screen_thread.join(timeout=0.5)#

        current_screen = (current_screen + 1) % len(screens)#update the current screen index

        start_screen(current_screen)#start the next screen


def joystick_pressed(channel):#joystick pressed callback function
    global press_count#declare the global variable

    press_count += 1#increment the press count
    print(f"Joystick pressed {press_count} times")#print the press count

    switch_to_next_screen()


def main():#main function
    global stop_event, screen_thread#declare the global variables

    GPIO.setmode(GPIO.BCM)#set the gpio mode to bcm
    GPIO.setup(JOY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)#

    GPIO.add_event_detect(
        JOY_BUTTON,#joystick button pin
        GPIO.FALLING,#trigger the event on a falling edge
        callback=joystick_pressed,#joystick pressed callback function
        bouncetime=200#time to wait before triggering the event again
    )

    start_screen(current_screen)#start the first screen

    try:
        while True:#infinite loop to keep the program running
            time.sleep(1)#wait for 1 second

    except KeyboardInterrupt:#catch keyboard interrupt
        print("Exiting...")#print exiting message

    finally:#finally block to clean up
        if stop_event is not None:#stop the current screen if it is running
            stop_event.set()

        if screen_thread is not None and screen_thread.is_alive():#wait for the current screen to finish
            screen_thread.join(timeout=0.5)#

        GPIO.cleanup()#cleanup the gpio pins


if __name__ == "__main__":#run the main function
    main()