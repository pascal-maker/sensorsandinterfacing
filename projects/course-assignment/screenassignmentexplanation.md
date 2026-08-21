lets explain the assignment screen: 
first we import the libraries we need: time for delays threading for running the screens in different threads RPi.GPIO for controlling the GPIO pins and the screen files we need for each screen
then we define the screens list which contains the run function of each screen in order
 then we define the current screen index press count and screen thread and stop event
 then we define the switch lock which is used to prevent race conditions when switching screens
 then we define the start screen function which starts the screen at the given index
 then we define the switch to next screen function which switches to the next screen
 then we define the joystick pressed function which is called when the joystick is pressed
 then we define the main function which sets up the GPIO pins and starts the first screen
 we start the first screen and wait for the joystick to be pressed
 when the joystick is pressed we switch to the next screen
 we continue this process until the user presses the joystick 6 times
  