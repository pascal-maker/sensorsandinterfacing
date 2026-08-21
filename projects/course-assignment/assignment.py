import time#used to add delays
import threading#used to run the screens in different threads
import smbus#used to communicate with the adc over i2c
import RPi.GPIO as GPIO#used to control the GPIO pins

import screen1#import the first screen ip address
import screen2#import the second screen lcd
import screen3#import the third screen joystick & button & adc & rgb led
import screen4#import the fourth screen MPU6050 & lcd
import screen5#import the fifth screen distance sensor & lcd
import screen6#import the sixth screen ble uart & lcd

# Joystick button pin
JOY_BUTTON = 7#joystick button pin

# ADC settings
ADC_ADDR = 0x48#adc address
X_CHANNEL = 5#joystick x channel (check with test script if unsure)
Y_CHANNEL = 4#joystick y channel (check with test script if unsure) #potentiometer y axis

# RGB LED pins
RED_PIN = 5#red led pin
GREEN_PIN = 6#green led pin
BLUE_PIN = 13#blue led pin
#we use 3 pins for rgb to create colors we make them inverse becasue they are connected to gnd
bus = smbus.SMBus(1)#initialize the i2c bus pi communcite with ADC LCD sensors

screens = [
    screen1.run,#list of screens to run
    screen2.run,#
    screen3.run,
    screen4.run,
    screen5.run,
    screen6.run,
]
#list of screens to run in the main eeasier to switchs screen dynamically
current_screen = 0#current screen index
press_count = 0#number of times the joystick has been pressed
screen_thread = None#thread that runs the current screen
stop_event = None#event to stop the current screen

switch_lock = threading.Lock()#lock to prevent race conditions when switching screens
#Joystick
#↓
#ADC reads movement
#↓
#Main program changes screen
#↓
#Selected screen runs
#↓
#LCD displays content

def ads7830_command(channel):#create the command for the adc
    return 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)#create the command for the adc


def read_adc(channel):#read the adc value
    bus.write_byte(ADC_ADDR, ads7830_command(channel))#send the command to the adc
    time.sleep(0.005)#wait a tiny bit
    return bus.read_byte(ADC_ADDR)#read the value from the adc


def convert_to_percentage(value):#convert the ADC value to percentage
    return (value / 255) * 100#return percentage easier to undertsand and for rgb led brightness


def set_rgb(red_pwm, green_pwm, blue_pwm, red, green, blue):#set the rgb led values
    #this controls the RGB LED brightnesss
    #for example:
    #10% duty cycle = LED is ON 10% of the time (dim)
    #90% duty cycle = LED is ON 90% of the time (bright)
    red_pwm.ChangeDutyCycle(100 - red)#set the red led duty cycle controls brightness.
    #same logic applied to green and blue
    green_pwm.ChangeDutyCycle(100 - green)#set the green led duty cycle common anode logic is inverted so we subtract from 100 0 fully on and 100 fully off so if red is 100 we send 0 so it is fully on
    blue_pwm.ChangeDutyCycle(100 - blue)#set the blue led duty cycle


def setup_gpio():#setup the gpio pins and pwm
    GPIO.setmode(GPIO.BCM)#set the mode to bcm
    GPIO.setwarnings(False)#disable warnings

    GPIO.setup(JOY_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setup the joystick button as input with pull-up

    GPIO.setup(RED_PIN, GPIO.OUT)#set the red led pin as output
    GPIO.setup(GREEN_PIN, GPIO.OUT)#set the green led pin as output
    GPIO.setup(BLUE_PIN, GPIO.OUT)#set the blue led pin as output

    red_pwm = GPIO.PWM(RED_PIN, 1000)#set the red led pwm frequency is 1000hz
    #same logic applied to green and blue
    green_pwm = GPIO.PWM(GREEN_PIN, 1000)#set the green led pwm
    blue_pwm = GPIO.PWM(BLUE_PIN, 1000)#set the blue led pwm

    red_pwm.start(0)#start the red led pwm with 0% duty cycle (off)
    #same logic applied to green and blue
    green_pwm.start(0)#start the green led pwm with 0% duty cycle (off)
    blue_pwm.start(0)#start the blue led pwm with 0% duty cycle (off)

    return red_pwm, green_pwm, blue_pwm#return the pwm objects


def start_screen(index):#start the screen at the given index
    global screen_thread, stop_event#declare the global variables

    stop_event = threading.Event()#create a stop event
    #Q1 — why a separate thread (BLE loop would block the main loop, LCD freezes)
    #Q2 — queue vs plain variable (thread safety — two threads can't safely share a plain variable)
    #Q3 — timeout=0.1 (prevents blocking forever, raises queue.Empty which is caught and ignored)
    #Q4 — bytes and errors="ignore" (BLE sends raw bytes, bad UTF-8 would crash without the flag)
    #Q5 — daemon=True (thread closes automatically when main thread exits, otherwise program never exits)
    #create a thread for the screen
    screen_thread = threading.Thread(#
        target=screens[index],#target is the screen to run
        args=(stop_event,),#arguments to pass to the screen
        daemon=True#set as a daemon thread so it will close when the main thread closes
    )

    screen_thread.start()#start the thread
    print(f"Started screen {index + 1}")#print the screen number


def switch_to_next_screen():#switch to the next screen
    global current_screen, screen_thread, stop_event#declare the global variables can be used    in multiple places

    with switch_lock:#lock to prevent race conditions when switching screens
        if stop_event is not None:#stop the current screen if it is running
            stop_event.set()#setting stop event to true means  the current thread will be terminated 

        if screen_thread is not None and screen_thread.is_alive():#wait for the current screen to finish
            screen_thread.join(timeout=0.5)#waits for 0.5 seconds for the current screen to finish

        current_screen = (current_screen + 1) % len(screens)#update the current screen index

        start_screen(current_screen)#start the next screen


def joystick_pressed(channel):#joystick pressed callback function
    global press_count#declare the global variable

    press_count += 1#increment the press count
    print(f"The joystick has been pressed {press_count} times!")#print the press count

    switch_to_next_screen()#switch to the next screen

#Current screen running
#        ↓
#Joystick pressed
#        ↓
#Tell old screen to stop
#        ↓
#Wait for old screen to finish
#        ↓
#Move to next screen index
#        ↓
#Start next screen
def main():#main function
    global stop_event, screen_thread#declare the global variables used for screen switching and tracking running screen thread

    red_pwm, green_pwm, blue_pwm = setup_gpio()#setup the gpio pins and pwm prepres joystick button,rgb le dpons pwm ledbrightness control

    GPIO.add_event_detect(#inteerupt event system detects when the joystick is pressed
        JOY_BUTTON,#joystick button pin
        GPIO.FALLING,#trigger the event on a falling edge
        callback=joystick_pressed,#joystick pressed callback function
        bouncetime=200#time to wait before triggering the event again
    )

    start_screen(current_screen)#start the first screen

    try:
        while True:#infinite loop to keep the program running
            x_value = read_adc(X_CHANNEL)#read the x-axis value from the joystick
            y_value = read_adc(Y_CHANNEL)#read the y-axis value from the joystick

            red = convert_to_percentage(x_value)#x-axis controls the red color
            green = convert_to_percentage(y_value)#y-axis controls the green color
            blue = (red + green) / 2#blue is the average of red and green

            set_rgb(red_pwm, green_pwm, blue_pwm, red, green, blue)#update the rgb led brightness based on joystick position

            time.sleep(0.1)#wait a tiny bit before the next read

    except KeyboardInterrupt:#catch keyboard interrupt
        print("Exiting...")#print exiting message

    finally:#finally block to clean up
        if stop_event is not None:#stop the current screen if it is running
            stop_event.set()#sets the stop event to true telling the current screen to stop 

        if screen_thread is not None and screen_thread.is_alive():#waits for the current screen to finish
            screen_thread.join(timeout=0.5)#waits for 0.5 seconds for the current screen to finish

        red_pwm.stop()#stop the red led pwm
        green_pwm.stop()#stop the green led pwm
        blue_pwm.stop()#stop the blue led pwm

        GPIO.cleanup()#cleanup the gpio pins


if __name__ == "__main__":#run the main function
    main()
#Joystick movement
#↓
#ADC reads X/Y
#↓
#Convert to RGB percentages
#↓
#RGB LED changes color
#
#Joystick button
#↓
#Interrupt triggers callback
#↓
#Switch LCD screen thread
#↓
#New screen displayed