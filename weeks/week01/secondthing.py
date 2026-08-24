import time
  from RPi import GPIO

  # Use BCM GPIO numbers, such as GPIO 17 and GPIO 20.
  GPIO.setmode(GPIO.BCM)

  # Store the GPIO pin numbers.
  btn = 20
  led = 17

  # Configure GPIO 20 as an input for the button.
  #
  # GPIO.IN means that the Raspberry Pi reads a signal from this pin.
  #
  # pull_up_down=GPIO.PUD_UP enables the Raspberry Pi's internal pull-up resistor.
  # This keeps the input HIGH (1) while the button is not pressed.
  #
  # The button should connect GPIO 20 to GND when pressed. Pressing it therefore
  # changes the input from HIGH (1) to LOW (0). This is called active-LOW.
  GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)

  # Configure GPIO 17 as an output for controlling the LED.
  GPIO.setup(led, GPIO.OUT)

  try:
      # Continue running until the user presses Ctrl+C.
      while True:

          # Read the button pin.
          # Not pressed = GPIO.HIGH (1)
          # Pressed     = GPIO.LOW  (0)
          value = GPIO.input(btn)

          # Invert the button value before sending it to the LED.
          #
          # Button not pressed:
          # value = 1, not value = False (0), LED off
          #
          # Button pressed:
          # value = 0, not value = True (1), LED on
          GPIO.output(led, not value)

          # Print the GPIO pin number and its current value.
          print("The value of pin {0} is {1}".format(btn, value))

          # Wait half a second before reading the button again.
          time.sleep(0.5)

  except KeyboardInterrupt:
      # Ctrl+C stops the program without showing an error.
      print("\nCtrl+C received. Stopping...")

  finally:
      # Return the GPIO pins to their safe default state.
      # This executes even when Ctrl+C stops the program.
      GPIO.cleanup()
      print("GPIO cleanup complete.")