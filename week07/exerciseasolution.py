from time import sleep#importing the sleep function
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)#setting the mode to BCM

pins = (19,13,6,5)#setting the pins for the stepper motor
GPIO.setup(pins, GPIO.OUT)#setting the pins as output

BUTTON = 20#setting the button pin
stepper_speed = 0.005#setting the speed of the stepper motor

GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting the button pin as input

steps = (
    (1, 0, 0, 0),#coil one is on
    (1, 1, 0, 0),#coil one and coil two are on
    (0, 1, 0, 0),#coil two is on
    (0, 1, 1, 0),#coil two and coil three are on
    (0, 0, 1, 0),#coil three is on
    (0, 0, 1, 1),#coil three and coil four are on
    (0, 0, 0, 1),#coil four is on
    (1, 0, 0, 1),#coil four and coil one are on
)

motor_running = False#setting the motor running to false

try:
    while True:#infinite loop

        if GPIO.input(BUTTON) == 0:#checking if the button is pressed

            if not motor_running:#checking if the motor is not running
                print("Motor turning left")#printing the motor turning left
                motor_running = True#setting the motor running to true

            for step in reversed(steps):#setting the steps for the motor here reversed is used for counter clockwise rotation (opposite direction of clockwise) so to the left

                if GPIO.input(BUTTON) != 0:#checking if the button is not pressed
                    print("Button released - motor stopped")#printing the button released motor stopped
                    motor_running = False#setting the motor running to false
                    break#breaking the loop

                for i in range(4):#setting the pins to 1 or 0 handles all 4 motor pins one by one
                    GPIO.output(pins[i], step[i])#sets the pins to 1 or 0

                sleep(stepper_speed)#waits for the stepper speed

        else:
            for pin in pins:#looping through the pins
                GPIO.output(pin, 0)#sets the pins to 0

except KeyboardInterrupt:#handling the keyboard interrupt
    GPIO.cleanup()#cleaning up the GPIO pins
    print("Stepper motor stopped by user")#printing the stepper motor stopped by user