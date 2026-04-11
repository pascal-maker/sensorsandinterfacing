from time import sleep
from RPi import GPIO

GPIO.setmode(GPIO.BCM)#setting the mode to BCM
GPIO.setwarnings(False)#setting the warnings to false
pins = (19, 13, 6, 5)#setting the pins

GPIO.setup(pins, GPIO.OUT)#setting the pins as output

BUTTON = 21
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the button pin as input

steps = (
    (1, 0, 0, 0),#setting the steps for the motor
    (1, 1, 0, 0),# coil one is on and coil two is on
    (0, 1, 0, 0),# coil two is on
    (0, 1, 1, 0),# coil two is on and coil three is on
    (0, 0, 1, 0),# coil three is on
    (0, 0, 1, 1),# coil three is on and coil four is on
    (0, 0, 0, 1),# coil four is on
    (1, 0, 0, 1),# coil four is on and coil one is on
)

try:
    while True:
        if GPIO.input(BUTTON) == 0:#checking if the button is pressed
            for step in  reversed(steps):#reversing the steps for the motor
                for i in range(4):#setting the pins to 1 or 0 handles all 4 motor pins one by one
                    GPIO.output(pins[i], step[i])#setting the pins to 1 or 0 handles all 4 motor pins one by one send the value from step[i] to the GPIO pin pins[i]#So each pin gets the matching ON/OFF value.
                sleep(0.02)#waiting for 0.02 seconds
        else:
            for pin in pins:#setting the pins to 0
                GPIO.output(pin, 0)        #setting the pins to 0 handles all 4 motor pins one by one
except KeyboardInterrupt:
    GPIO.cleanup()
    print("Stepper motor stopped by user")
