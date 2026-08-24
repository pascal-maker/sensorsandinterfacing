led = 21                  # Store GPIO pin 21 in the variable 'led'

from RPi import GPIO      # Import the GPIO library

GPIO.setmode(GPIO.BCM)    # Use BCM numbering, so pin 21 means GPIO21

GPIO.setup(led, GPIO.OUT) # Set GPIO21 as an output pin

GPIO.output(led, GPIO.HIGH)  # Send HIGH (3.3V) to the pin -> LED turns on
GPIO.output(led, GPIO.LOW)   # Send LOW (0V) to the pin -> LED turns off

GPIO.cleanup(led)         # Reset only GPIO21
exit()                    # Stop the program