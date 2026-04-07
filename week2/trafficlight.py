from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)#set the mode of the GPIO pins to BCM

# Buttons
button1 = 20#button 1 is connected to GPIO pin 20


# LEDs
led1 = 9#GREEN LIGHT
led2 = 10#YELLOW LIGHT
led3 = 11#RED LIGHT
GPIO.setup(button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)#set button 1 as input with pull up resistor
GPIO.setup(led1, GPIO.OUT)#set led 1 as output
GPIO.setup(led2, GPIO.OUT)#set led 2 as output
GPIO.setup(led3, GPIO.OUT)#set led 3 as output
prev_button1 = GPIO.input(button1)#previous state of button 1

#main loop
try:
    while True:
        current_button1 = GPIO.input(button1)#current state of button 1

        if current_button1 == GPIO.LOW and prev_button1 == GPIO.HIGH:#if button 1 is pressed
                GPIO.output(led1, GPIO.HIGH)#turn on green light
                GPIO.output(led2, GPIO.LOW)#turn off yellow light
                GPIO.output(led3, GPIO.LOW)#turn off red light
                print("Button1 press -> Green Light")#print message
                time.sleep(5)#wait for 1 second
                GPIO.output(led1, GPIO.LOW)#turn off green light
                GPIO.output(led2, GPIO.HIGH)#turn on yellow light
                GPIO.output(led3, GPIO.LOW)#turn off red light
                print("Button2 press -> Yellow Light")#print message
                time.sleep(1)#wait for 1 second
                GPIO.output(led1, GPIO.LOW)#turn off green light
                GPIO.output(led2, GPIO.LOW)#turn off yellow light
                GPIO.output(led3, GPIO.HIGH)#turn on red light
                print("Button3 press -> Red Light")#print message
                time.sleep(4)#wait for 1 second
                GPIO.output(led1, GPIO.LOW)#turn off green light
                GPIO.output(led2, GPIO.LOW)#turn off yellow light
                GPIO.output(led3, GPIO.LOW)#turn off red light
                print("Button1 not pressed -> All LEDs off")#print message
                time.sleep(1)#wait for 1 second
        prev_button1 = current_button1    
                
            

except KeyboardInterrupt:
    print("Exiting program")

finally:
    GPIO.cleanup()