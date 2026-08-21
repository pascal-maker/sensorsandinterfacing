"""Use the 4 buttons connected to GPIO20, GPIO21, GPIO16 and GPIO26.
When pressed on the bottom button: turn the led off
When pressed on the upper button: turn led on (steady)
When pressed on the left button: blink led slow
When pressed on the right button: blink led fast
> until another action is made; or the program is stopped
"""
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# pin numbers
btn1 = 21# bottom button
btn2 = 20# upper button
btn3 = 16# left button
btn4 = 26# right button
LED  = 17# the led

# setup pins
GPIO.setup(btn1, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting up the button as input with pull up resistor
GPIO.setup(btn2, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting up the button as input with pull up resistor
GPIO.setup(btn3, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting up the button as input with pull up resistor
GPIO.setup(btn4, GPIO.IN, pull_up_down=GPIO.PUD_UP)#setting up the button as input with pull up resistor
GPIO.setup(LED, GPIO.OUT)#setting up the led as an output out means on High means on , off means low

#initial state
mode = "off"#intializing the mode as off because when the program starts, it needs to know what to do with the LED before any button is pressed.
try:
    while True:#Infinite loop only stops with ctrl + c

      #Read Button1
      if GPIO.input(btn1) == GPIO.LOW:#we do input here because the button is connected to the ground and we are using pull up resistors so the button isHIGH when not pressed and LOW when pressed.  If you checked for GPIO.HIGH instead, your code would trigger when the button is not pressed, which is the opposite of what you want.
        time.sleep(0.05)
        print("Led off")
        mode = "off"# changing mode to off

      elif GPIO.input(btn2) == GPIO.LOW:
        time.sleep(0.05)
        print(" Led on")    
        mode = "on"# changing mode to on

      elif GPIO.input(btn3) == GPIO.LOW:
        time.sleep(0.2)
        mode = "blink faster"
        
      elif GPIO.input(btn4) == GPIO.LOW:
        time.sleep(0.2)# we do the same here because it also delays the output code payses letting the button stelle befoee continunng by the time the loops runs agaun , the bouncing is over.
        mode = "blink slower"

      #execute mode
      if mode == "on":#changing mode to on
        GPIO.output(LED,GPIO.HIGH)#setting led to high
      elif mode == "off":#changing mode to off
        GPIO.output(LED,GPIO.LOW)#setting led to low
      elif mode == "blink faster":# changing mode to blink faster
        GPIO.output(LED, not GPIO.input(LED))#  reads the current state of the led high or low , flips it high ebcomes low , low becomes high writes that filled value back to the led combined with time.sleep this creates the blinking effect it just keeps flipping the led state witha pause in between.
        print("blink faster button pressed")#printing the mode
        
        time.sleep(0.1)# blink faster the led toggles every 100 milliseconds which means it blinks 10 times per second making it blink faster.
      elif mode == "blink slower":# changing mode to blink slower
        print("blink slower button pressed")#printing the mode
        GPIO.output(LED, not GPIO.input(LED))#reads the current state of the led high or low , flips it high ebcomes low , low becomes high writes that filled value back to the led combined with time.sleep this creates the blinking effect it just keeps flipping the led state witha pause in between.
        time.sleep(0.5)# blink slower the led toggles every 500 milliseconds which means it blinks 2 times per second making it blink slower.
        

except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()
   
#the reason why we do not use mode for buttons 3 and 4 is because they are blinking buttons which means they are alwyas on and off. if we used the mode for buttons 3 and 4 the led would only blink once and then turn off. by not using the mode , the led will continue to blink until another button is pressed. 
#GPIO.output(LED, not GPIO.input(LED))# it just keeps flipping the led state witha pause in between. if we used the mode for buttons 3 and 4 the led would only blink once and then turn off. now with this the led will continue to blink until another button is pressed. 
# time.sleep(0.2)#we do the same here because it also delays the output code payses letting the button stelle befoee continunng by the time the loops runs agaun , the bouncing is over.