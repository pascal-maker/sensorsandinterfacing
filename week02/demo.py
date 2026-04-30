import time
from RPi import GPIO

LED = 17 # GPIO 17
BTN = 20 # GPIO 20

GPIO.setmode(GPIO.BCM) # set the GPIO mode
GPIO.setup(BTN,GPIO.IN,pull_up_down=GPIO.PUD_UP) # setup the button as input with pull-up
GPIO.setup(LED,GPIO.OUT) # setup the LED as output

led_state = GPIO.LOW # set the initial state of the LED to low you track the state yourself in software
previous_btn_state = GPIO.input(BTN) #  reads the actual current state of the button   this the baseline you campare against in your loop you can only detect a press low-> high or high-> low transition  if you know what the state was before
n_presses = 0 # initialize the number of button presses to 0 standard counter initialization
GPIO.output(LED,led_state) # set the initial state of the LED drives the hardware pin to match your software variable. we set to low so the led is initially off and hardware and software are in sync
try:
    while True:
        current_btn_state = GPIO.input(BTN) # get the current state of the button
        if previous_btn_state == GPIO.HIGH and current_btn_state == GPIO.LOW: # detect a falling edge when the signal goes from high-> low extact moment the button is pressed you can only react to extact transitions
            time.sleep(0.01) # wait for the button to settle
            if GPIO.input(BTN) == GPIO.LOW: # confirm the button is still pressed
                led_state = not led_state # toggle the LED state updates the software variable not gpio.low gives true high not gpio.high false low this keeps teack of what teh eld should be in the python memory this is not setting the pin it is updating the python variable
                GPIO.output(LED,led_state) # set the new state of the LED drives the physical pin based on the python variable. it pushes it into hardware.
                n_presses += 1 # increment the number of button presses
                print(f"Button was pressed {n_presses} times.") # print the number of button presses
        previous_btn_state = current_btn_state # update the previous state of the button this is what makes edge detection work on the next loop interation. would never change and you would never detect a transition it lets you detect change.
        time.sleep(0.1) # wait for the button to settle
except KeyboardInterrupt:
    print("Keyboard interrupt received, exiting...")#
finally:
    print("Cleaning up GPIO and exiting...")
    GPIO.cleanup() # clean up the GPIO pins