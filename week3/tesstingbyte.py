import RPi.GPIO as GPIO   # Import library to control GPIO pins
import time               # Import time module for delays

GPIO.setmode(GPIO.BCM)   # Use BCM numbering (GPIO numbers)

rx_pin = 15              # Define the receive pin (we will read bits from this pin)

# Configure rx_pin as input with internal pull-up resistor
# This means default value = 1, and becomes 0 when connected to GND
GPIO.setup(rx_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def shift_byte_in():
    """
    Receive 1 byte serially (bit by bit)
    NOTE: This version shifts left each time → MSB-first style reconstruction
    """
    data = 0  # Start with empty byte (00000000)

    for i in range(8):  # Loop 8 times (one for each bit)
        
        # Read one bit from the input pin (0 or 1)
        bit = GPIO.input(rx_pin)
        
        # Shift existing data 1 position to the left
        # Then insert the new bit on the right (LSB)
        # Example:
        # data = 00000001
        # new bit = 1
        # → (data << 1) = 00000010
        # → OR with bit → 00000011
        data = (data << 1) | bit
        
        # Small delay to allow time between bit reads
        time.sleep(0.5)

    return data  # Return the reconstructed byte

try:
    while True:  # Infinite loop to keep reading bytes
        
        # Read one full byte from serial input
        value = shift_byte_in()
        
        # Print the received byte in binary format
        print(f"Received byte: {bin(value)}")
        
        # Wait before reading next byte
        time.sleep(2)

# Stop safely when CTRL + C is pressed
except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()  # Reset GPIO pins

# Always clean up GPIO when program ends
finally:
    GPIO.cleanup()