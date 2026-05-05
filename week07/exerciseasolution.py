from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)#setting the mode to BCM
pins = (19,13,6,5)#setting the pins for the motor
GPIO.setup(pins, GPIO.OUT)#setting the pins as output
BUTTON = 20#setting the button pin turn the stepper motor left until released
stepper_speed=0.005
GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the button pin as input
steps = (
    (1, 0, 0, 0),#setting the steps for the motor
    (1, 1, 0, 0),# coil one is on and coil two is on
    (0, 1, 0, 0),# coil two is on
    (0, 1, 1, 0),# coil two is on and coil three is on
    (0, 0, 1, 0),# coil three is on
    (0, 0, 1, 1),# coil three is on and coil four is on
    (0, 0, 0, 1),# coil four is on
    (1, 0, 0, 1),#coil four is on and coil one is on
)

try:
    while True:
        if GPIO.input(BUTTON) == 0:#checking if the button is pressed
            for step in reversed(steps):#setting the steps for the motor
                if GPIO.input(BUTTON) != 0:#checking if the button is released
                    break#breaking the loop
                for i in range(4):#setting the pins to 1 or 0 handles all 4 motor pins one by one
                    GPIO.output(pins[i], step[i])#reverses the order of the pins
                sleep(0.005)#waiting for the stepper speed in seconds
        else:
            for pin in pins:#setting the pins to 0
                 GPIO.output(pin, 0)#setting the pins to 0 handles all 4 motor pins one by one

except KeyboardInterrupt:#keyboard interrupt
    GPIO.cleanup()#cleaning up the pins
    print("Stepper motor stopped by user")#printing the stepper motor stopped by user