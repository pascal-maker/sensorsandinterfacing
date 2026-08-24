from RPi import GPIO

# Use BCM numbering (GPIO numbers, not physical pin numbers)
GPIO.setmode(GPIO.BCM)
try:
     #Store the GPIO pin number for the button
    btn = 9

    # Set button pin as input
    # PUD_UP activates the internal pull-up resistor:
    # default state = HIGH (1)
    # pressed state = LOW (0) if button is connected to GND
    GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Read the current value of the button pin
    value = GPIO.input(btn)

    # Print the button pin number and its value
    print('The value of pin {0} is {1}'.format(btn, value))

    # Store the GPIO pin number for the LED
    led = 10

    # Set LED pin as output
    GPIO.setup(led, GPIO.OUT)

   # Output the opposite of the button value to the LED
    # If button = 1 (not pressed), LED gets False = OFF
    # If button = 0 (pressed), LED gets True = ON
    GPIO.output(led, not value)

   # Print the LED pin. number and the value sent to it
    print('The value of pin {0} is {1}'.format(led, not value))
   
except KeyboardInterrupt:
    pass
finally:
    # Clean up the LED pin after use
    GPIO.cleanup(led)
    

    

#