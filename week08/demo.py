import RPi.GPIO as GPIO   # library to control Raspberry Pi GPIO pins
import time               # library for delays

DS = 22    # Serial Data pin of the shift register
SHCP = 17  # Shift Clock pin
STCP = 27  # Storage Clock / Latch pin

GPIO.setmode(GPIO.BCM)         # use BCM pin numbering
GPIO.setup(DS, GPIO.OUT)       # set DS as output
GPIO.setup(SHCP, GPIO.OUT)     # set SHCP as output
GPIO.setup(STCP, GPIO.OUT)     # set STCP as output

def write_bit(bit):
    GPIO.output(DS, bit)   # put the bit (0 or 1) on the data pin
    GPIO.output(SHCP, 0)   # make sure shift clock starts LOW
    GPIO.output(SHCP, 1)   # rising edge: shift register reads DS

def write_byte(value):
    for i in range(7, -1, -1):   # go through the 8 bits from left to right
        bit = (value >> i) & 1   # take 1 bit from the byte
        write_bit(bit)           # send that bit to the shift register

def latch():
    GPIO.output(STCP, 0)   # make sure latch clock starts LOW
    GPIO.output(STCP, 1)   # rising edge: copy shift register to outputs

try:
    while True:
        write_byte(0b10000000)   # only first output HIGH
        latch()                  # show data on outputs
        time.sleep(1)            # wait 1 second

        write_byte(0b00000000)   # all outputs LOW
        latch()                  # show data on outputs
        time.sleep(1)            # wait 1 second

        write_byte(0b11111111)   # all outputs HIGH
        latch()                  # show data on outputs
        time.sleep(1)            # wait 1 second

except KeyboardInterrupt:
    pass   # stop program with Ctrl+C

finally:
    GPIO.cleanup()   # reset GPIO pins neatly