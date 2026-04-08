import RPi.GPIO as GPIO   # Import Raspberry Pi GPIO library
import time               # Import time module for delays

GPIO.setmode(GPIO.BCM)   # Use BCM pin numbering (GPIO numbers, not physical pins)

tx_pin = 14              # Define the transmit pin (we will send bits through this pin)

GPIO.setup(tx_pin, GPIO.OUT)  # Configure tx_pin as an output pin

def shift_byte_out(data):
    """
    Send 1 byte serially (bit by bit), starting from the LSB (Least Significant Bit)
    """
    for i in range(8):   # Loop over all 8 bits of the byte (0 → 7)
        
        # Extract bit i from the data
        # Step 1: shift data i positions to the right
        # Step 2: mask with & 1 to keep only the last bit
        bit = (data >> i) & 1
        
        # Send the extracted bit to the GPIO pin (0 or 1)
        GPIO.output(tx_pin, bit)
        
        # Print which bit is being sent (for debugging/learning)
        print(f"bit {i}: sent {bit}")
        
        # Small delay so we can observe the output (not too fast)
        time.sleep(0.5)

try:
    while True:  # Infinite loop to continuously send the byte
        
        value = 0b10110010   # Define the byte to send (binary format)
        
        # Print the byte being sent
        print(f"Sending byte: {bin(value)}")
        
        # Call the function to send the byte bit by bit
        shift_byte_out(value)
        
        # Wait before sending again
        time.sleep(2)

# If user presses CTRL + C → stop the program safely
except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()  # Reset GPIO pins (important cleanup)

# Always run cleanup at the end (even if error occurs)
finally:
    GPIO.cleanup()