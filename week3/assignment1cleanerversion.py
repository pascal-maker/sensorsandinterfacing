import RPi.GPIO as GPIO   # Import library to control GPIO pins
import time               # Import time module for delays

GPIO.setmode(GPIO.BCM)   # Use BCM numbering (GPIO numbers)

# List of GPIO pins connected to BCD lines (1, 2, 4, 8)
pins = [16, 20, 21, 26]  # Utilize a list for the 4 inputs

# Configure each pin as input with internal pull-up resistor
for pin in pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

last_value = None  # Store previous value to detect changes

try:
    while True:
        value = 0      # Initialize the final BCD value
        bits = []      # List to store individual bits for printing

        # Loop over the 4 BCD input pins
        for i in range(4):
            
            # Read the pin and invert it:
            # pull-up → default = 1, active = 0 → so we invert
            bit = int(not GPIO.input(pins[i]))
            
            bits.append(bit)  # Store the bit in the list
            
            print(f"bit {i} = {bit}")  # Print each bit for debugging
            
            # Place the bit in the correct position and combine it into value
            # Example: bit=1, i=2 → 1 << 2 = 4 → added to value
            value |= bit << i

        # Only print when the value changes
        if value != last_value:
            
            print(f"bit 0 = {bits[0]}")
            print(f"bit 1 = {bits[1]}")
            print(f"bit 2 = {bits[2]}")
            print(f"bit 3 = {bits[3]}")
            
            print(f"BCD value = {value}")  # Final decimal value
            
            print("----")
            
            last_value = value  # Update last value

        time.sleep(0.1)  # Small delay to avoid flooding output

# Stop program safely with CTRL + C
except KeyboardInterrupt:
    print("Exiting...")

# Always clean up GPIO pins
finally:
    GPIO.cleanup()