from time import sleep
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)

pins = (19,13,6,5)
GPIO.setup(pins, GPIO.OUT)#
steps = ((1,0,0,0),(1,1,0,0),(0,1,0,0),(0,1,1,0),(0,0,1,0),(0,0,1,1),(0,0,0,1),(1,0,0,1))

try:
    for n in range(512):
        for step in steps:
            for i in range(4):
                GPIO.output(pins[i], step[i])
    for n in range(512):
        for step in steps:
            for i in range(4):
                GPIO.output(pins[3-i], step[i])#reverse
            sleep(0.001)
    print("Stepper motor stopped")
except KeyboardInterrupt:
    print("Stepper motor stopped by user")
    GPIO.cleanup()
    
                
                    