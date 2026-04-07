from RPi import GPIO
import time

GPIO.setmode(GPIO.BCM)#set the mode of the GPIO pins to BCM

ped_button = 21#pedestrian button is connected to GPIO pin 21
#leds
led_green = 9
led_yellow= 10
led_red = 11

GPIO.setup(ped_button, GPIO.IN, pull_up_down=GPIO.PUD_UP)#set pedestrian button as input with pull up resistor
GPIO.setup(led_green, GPIO.OUT)#set green led as output
GPIO.setup(led_yellow, GPIO.OUT)#set yellow led as output
GPIO.setup(led_red, GPIO.OUT)#set red led as output

prev_ped_button = GPIO.input(ped_button)#previous state of pedestrian button
try:
    while True:
        GPIO.output(led_green, GPIO.HIGH)#turn on green led
        GPIO.output(led_yellow, GPIO.LOW)#turn off yellow led
        GPIO.output(led_red, GPIO.LOW)#turn off red led
        
        green_start = time.time()
        while time.time() - green_start < 5:#green light for 5 seconds
            current_ped_button = GPIO.input(ped_button)#current state of pedestrian button
            #pedestrian button is pressed AND green light is on
            if current_ped_button == GPIO.LOW and prev_ped_button == GPIO.HIGH:#if pedestrian button is pressed
                print("Pedestrian button pressed")#print message
                
                #go to yellow
                GPIO.output(led_green, GPIO.LOW)#turn off green led
                GPIO.output(led_yellow, GPIO.HIGH)#turn on yellow led
                time.sleep(1)#wait for 1 second
                #go to red
                GPIO.output(led_yellow, GPIO.LOW)#turn off yellow led
                GPIO.output(led_red, GPIO.HIGH)#turn on red led
                time.sleep(4)#wait for 4 seconds


                prev_ped_button = GPIO.input(ped_button)#update previous state of pedestrian button
                time.sleep(0.1)#wait for 0.05 seconds
               
            else:
                #normal cycle  if no pedestrian pressed
                GPIO.output(led_green, GPIO.LOW)
                GPIO.output(led_yellow, GPIO.HIGH)
                GPIO.output(led_red, GPIO.LOW)
                print("Cars: YELLOW")
                time.sleep(1)

                GPIO.output(led_green, GPIO.LOW)
                GPIO.output(led_yellow, GPIO.LOW)
                GPIO.output(led_red, GPIO.HIGH)
                print("Cars: RED")
                time.sleep(4)
except KeyboardInterrupt:
    print("Exiting program")
    GPIO.cleanup()

                
