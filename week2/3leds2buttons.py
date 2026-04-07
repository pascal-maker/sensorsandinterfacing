from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)#set the mode of the GPIO pins to BCM

# Buttons
button1 = 20#button 1 is connected to GPIO pin 20
button2 = 21#button 2 is connected to GPIO pin 21

# LEDs
led1 = 9#led 1 is connected to GPIO pin 9
led2 = 10#led 2 is connected to GPIO pin 10
led3 = 11#led 3 is connected to GPIO pin 11

GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)#set button 1 as input with pull up resistor
GPIO.setup(button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)#set button 2 as input with pull up resistor

GPIO.setup(led1, GPIO.OUT)#set led 1 as output
GPIO.setup(led2, GPIO.OUT)#set led 2 as output
GPIO.setup(led3, GPIO.OUT)#set led 3 as output

# Start with all LEDs off
GPIO.output(led1, GPIO.LOW)#turn off led 1
GPIO.output(led2, GPIO.LOW)#turn off led 2
GPIO.output(led3, GPIO.LOW)#turn off led 3
#declaring variables
# State for button1 cycle
cycle_state = 0#state for button1 cycle

# Previous button states for edge detection so we can compare
prev_button1 = GPIO.input(button1)#previous state of button 1
prev_button2 = GPIO.input(button2)#previous state of button 2

# For blinking all LEDs while button2 is held
blink_state = False#software variable that stores whether all LEDs should be on or off
last_blink_time = time.time()#time of last blink
blink_interval = 0.3#interval between blinks
#function to set leds according to button1 cycle state
def set_cycle_leds(state):
    """Set LEDs according to button1 cycle state."""
    if state == 0:#if state is 0
        GPIO.output(led1, GPIO.HIGH)#turn on led 1
        GPIO.output(led2, GPIO.LOW)#turn off led 2
        GPIO.output(led3, GPIO.LOW)#turn off led 3
    elif state == 1:#if state is 1
        GPIO.output(led1, GPIO.LOW)#turn off led 1
        GPIO.output(led2, GPIO.HIGH)#turn on led 2
        GPIO.output(led3, GPIO.LOW)#turn off led 3
    elif state == 2:#if state is 2
        GPIO.output(led1, GPIO.LOW)#turn off led 1
        GPIO.output(led2, GPIO.LOW)#turn off led 2
        GPIO.output(led3, GPIO.HIGH)#turn on led 3
    elif state == 3:#if state is 3
        GPIO.output(led1, GPIO.LOW)#turn off led 1
        GPIO.output(led2, GPIO.LOW)#turn off led 2
        GPIO.output(led3, GPIO.LOW)#turn off led 3
#main loop
try:
    while True:
        current_button1 = GPIO.input(button1)#current state of button 1
        current_button2 = GPIO.input(button2)#current state of button 2

        # BUTTON 2 has priority WE START WITH BUTTON 2 FIRST EBCAUSE WHEN BUTTON 2 PRESSED ALL LEDS ARE TOGGLED TOGETHER
        if current_button2 == GPIO.LOW:#if button 2 is pressed
            # While holding button2: toggle all LEDs together
            now = time.time()#current time
            if now - last_blink_time >= blink_interval:#if time since last blink is greater than blink interval
                blink_state = not blink_state#toggle blink state
                GPIO.output(led1, blink_state)#turn on/off led 1
                GPIO.output(led2, blink_state)#turn on/off led 2
                GPIO.output(led3, blink_state)#turn on/off led 3
                last_blink_time = now#update last blink time

        else:
            # If button2 was just released: turn all LEDs off
            if prev_button2 == GPIO.LOW and current_button2 == GPIO.HIGH:#if button 2 was just released
                GPIO.output(led1, GPIO.LOW)#turn off led 1
                GPIO.output(led2, GPIO.LOW)#turn off led 2
                GPIO.output(led3, GPIO.LOW)#turn off led 3
                print("Button2 released -> all LEDs off")#print message



            # Button1 edge detection only when button2 is not being held
            #if button 1 is pressed NOW WE CHECK BUTTON 1
            if prev_button1 == GPIO.HIGH and current_button1 == GPIO.LOW:#if button 1 IS NOW PRESSED
                cycle_state = (cycle_state + 1) % 4#increment cycle state
                set_cycle_leds(cycle_state)#set leds according to cycle state

                if cycle_state == 0:#if cycle state is 0
                    print("Button1 press -> LED1 on")#print message
                elif cycle_state == 1:
                    print("Button1 press -> LED2 on")#print message
                elif cycle_state == 2:#if cycle state is 2
                    print("Button1 press -> LED3 on")
                elif cycle_state == 3:#if cycle state is 3
                    print("Button1 press -> all LEDs off")

                time.sleep(0.05)  # debounce

        prev_button1 = current_button1#update previous state of button 1
        prev_button2 = current_button2#update previous state of button 2

        time.sleep(0.01)#wait for 0.01 seconds

except KeyboardInterrupt:
    print("Exiting program")

finally:
    GPIO.cleanup()