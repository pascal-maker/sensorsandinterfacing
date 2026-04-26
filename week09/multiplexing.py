import time
import RPi.GPIO as GPIO

# 74HC595 pins These are the 3 pins connected to the 74HC595 shift register:
DS = 22      # serial data data pin that serially shifts in the bits
STCP = 27    # storage/latch clock the Q0-Q7 outputs only change when this pin is pulsed high
SHCP = 17    # shift clock pulse this pin high and low to clock each bit into the register
# DS   = the letter you type
# SHCP = press key to store each letter
# STCP = press Enter to display the word

# DS = when we type this we are sending the data for the letter to the shift register
# SHCP = press key to store each letter
# STCP = press Enter to display the word


class ShiftRegister:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(DS, GPIO.OUT)#setting gpio pins as outputs
        GPIO.setup(STCP, GPIO.OUT)
        GPIO.setup(SHCP, GPIO.OUT)

        GPIO.output(DS, GPIO.LOW)#setting gpio pins as low
        GPIO.output(STCP, GPIO.LOW)
        GPIO.output(SHCP, GPIO.LOW)

    def pulse(self, pin):
        GPIO.output(pin, GPIO.HIGH)#setting gpio pins as high
        time.sleep(0.000001)
        GPIO.output(pin, GPIO.LOW)#setting gpio pins as low
        time.sleep(0.000001)

    def shift_out_16bit(self, value):#shift out the value to the shift register
        # send MSB first: bit 15 → bit 0
        for i in range(15, -1, -1): #loop through the bits from 15 to 0
            bit = (value >> i) & 1#get the bit value
            GPIO.output(DS, GPIO.HIGH if bit else GPIO.LOW)#set the data pin
            self.pulse(SHCP)#pulse the shift clock

        # copy shifted data to outputs
        self.pulse(STCP)


ROWS = {#rows dictionary this tells us the bit position for each row 
    1: 1 << 0,#this is row 1 and its bit position is 0
    2: 1 << 1,#this is row 2 and its bit position is 1
    3: 1 << 2,#this is row 3 and its bit position is 2
    4: 1 << 3,#this is row 4 and its bit position is 3
    5: 1 << 4,#this is row 5 and its bit position is 4
    6: 1 << 5,  #this is row 6 and its bit position is 5
    7: 1 << 6,#this is row 7 and its bit position is 6
    8: 1 << 7,#this is row 8 and its bit position is 7
}

LETTER_A = [
    0b00111100,#this is the first row of the letter A these are the columns that will be lit up
    0b01000010,#this is the second row of the letter A
    0b01000010,#this is the third row of the letter A
    0b01111110,#this is the fourth row of the letter A
    0b01000010,#this is the fifth row of the letter A
    0b01000010,#this is the sixth row of the letter A
    0b01000010,#this is the seventh row of the letter A
    0b00000000,#this is the eighth row of the letter A
]

try:
    shift_reg = ShiftRegister()#creating an instance of the shift register

    while True: #looping through the rows
        for row in range(1, 9):#looping through the rows from 1 to 8
            row_byte = ROWS[row]#getting the row byte
            col_byte = LETTER_A[row - 1]#getting the column byte

            # If common anode matrix: invert columns
            col_byte = ~col_byte & 0xFF#inverting the column byte

            value = (row_byte << 8) | col_byte#combining the row and column bytes
            shift_reg.shift_out_16bit(value)#shifting out the value to the shift register

            time.sleep(0.001)#waiting for 0.001 seconds

except KeyboardInterrupt:
    GPIO.cleanup()#cleaning up the gpio pins

# 1. Activate row 1
# 2. Send columns for row 1
# 3. Activate row 2
# 4. Send columns for row 2
# ...
# 8. Repeat fast

