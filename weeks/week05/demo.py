import RPi.GPIO as GPIO#Imports the RPi.GPIO library
import time#Imports the time library

# --------------------------------------------------
# Configuration
# --------------------------------------------------

GPIO.setmode(GPIO.BCM)#Sets the GPIO mode to BCM

TX_PIN = 17          # GPIO pin connected to LED / receiver
BIT_TIME = 0.2       # 200 ms per bit

GPIO.setup(TX_PIN, GPIO.OUT)#Initializes the tx pin as output

GPIO.output(TX_PIN, 1)#Sets the tx pin to high


# --------------------------------------------------
# Send one bit
# --------------------------------------------------

def send_bit(bit):#Sends a single bit
    """
    Send a single bit.
    1 = HIGH
    0 = LOW
    """#Comments explaining the function
    GPIO.output(TX_PIN, bit)#Sets the tx pin to high or low depending on the bit value
    time.sleep(BIT_TIME)#Waits for the bit time to complete


# --------------------------------------------------
# Send one byte
# --------------------------------------------------

def send_byte(byte):#Sends a byte to the receiver
    """
    Send a byte using:
    - 1 start bit
    - 8 data bits
    - 1 stop bit

    UART style transmission.
    """

    print(f"\nSending byte: {byte}")#Prints the byte value
    print(f"Binary: {byte:08b}")#Prints the binary value of the byte

    # ----------------------------------------------
    # START BIT
    # UART start bit is LOW
    # ----------------------------------------------
    print("Start bit: 0")#Prints that the start bit is 0
    send_bit(0)#Sends the start bit

    # ----------------------------------------------
    # SEND DATA BITS
    # MSB first (bit 7 -> bit 0)
    # ----------------------------------------------
    for bit_position in range(7, -1, -1):#Loops through each bit position from 7 to 0

        shifted = byte >> bit_position#Shifts the byte to the right by the bit position
        bit = shifted & 1#Checks if the bit is 1 or 0

        print(
            f"Bit {bit_position}: "#Prints the bit position
            f"{byte:08b} >> {bit_position} "#Prints the byte value and the bit position
            f"= {shifted:b} -> {bit}"
        ) #Prints the bit position, byte value, shifted value, and bit value

        send_bit(bit)#Sends the bit value

    # ----------------------------------------------
    # STOP BIT
    # UART stop bit is HIGH
    # ----------------------------------------------
    print("Stop bit: 1")#Prints that the stop bit is 1
    send_bit(1)#Sends the stop bit


# --------------------------------------------------
# Send a string
# --------------------------------------------------

def send_string(text):#Sends a string to the receiver
    """
    Send all characters in a string.
    """

    for char in text:#Loops through each character in the string

        ascii_value = ord(char)#Gets the ASCII value of the character

        print("\n--------------------------------")
        print(f"Character: '{char}'")#Prints the character
        print(f"ASCII: {ascii_value}")#Prints the ASCII value

        send_byte(ascii_value)#Sends the ASCII value

        time.sleep(1)#Waits for 1 second before sending the next character


# --------------------------------------------------
# Main program
# --------------------------------------------------

try:

    message = "hello world"#Sets the message to "hello world"

    print("Starting transmission...")#Prints that the transmission is starting
    print(f"Message: {message}")#Prints the message

    send_string(message)#Sends the message

    print("\nTransmission complete.")#Prints that the transmission is complete

except KeyboardInterrupt:#If the keyboard interrupt is called

    print("\nProgram stopped by user.")#Prints that the program is stopped by user

finally:#The finally block is used to catch any errors that may occur

    GPIO.output(TX_PIN, 1)   #Sets the tx pin to high
    GPIO.cleanup()#Cleans up the GPIO pins

    print("GPIO cleaned up.")#Prints that the GPIO pins are cleaned up