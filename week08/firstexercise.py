import RPi.GPIO as GPIO
import time

DS = 22      # Serial Data pin
SHCP = 17    # Shift Clock pin
STCP = 27    # Storage Clock / Latch pin

def setup():
    GPIO.setmode(GPIO.BCM)          # use BCM pin numbering
    GPIO.setup(DS, GPIO.OUT)        # set DS as output
    GPIO.setup(SHCP, GPIO.OUT)      # set SHCP as output
    GPIO.setup(STCP, GPIO.OUT)      # set STCP as output

    GPIO.output(DS, 0)              # start data pin LOW
    GPIO.output(SHCP, 0)            # start shift clock LOW
    GPIO.output(STCP, 0)            # start storage clock LOW

def write_one_bit(bit):
    GPIO.output(DS, GPIO.HIGH if bit else GPIO.LOW)  # put 1 or 0 on data pin
    GPIO.output(SHCP, GPIO.HIGH)                     # rising edge shifts bit into register
    GPIO.output(SHCP, GPIO.LOW)                      # bring clock back LOW

def copy_to_storage_register():
    GPIO.output(STCP, GPIO.HIGH)   # rising edge copies shift register to outputs
    GPIO.output(STCP, GPIO.LOW)    # bring latch clock back LOW

def reset_storage_register():
    write_two_bytes(0, 0)          # send 16 zeros to clear both shift registers
    copy_to_storage_register()     # update outputs so all LEDs turn off

def write_one_byte(value):
    for i in range(7, -1, -1):     # go through bits from MSB to LSB
        bit = (value >> i) & 1     # extract one bit from the byte
        write_one_bit(bit)         # send that bit

def write_two_bytes(byte1, byte2):
    write_one_byte(byte1)          # send first byte
    write_one_byte(byte2)          # send second byte

setup()

try:
    for _ in range(8):
        write_one_bit(True)            # shift a 1 into the register
        copy_to_storage_register()     # show current shifted value on outputs
        time.sleep(1)

        reset_storage_register()       # turn everything off
        time.sleep(1)

        write_two_bytes(0b11111111, 0b11111111)  # set all 16 outputs HIGH
        copy_to_storage_register()               # update outputs
        time.sleep(2)

        write_two_bytes(0b00000000, 0b00001010)  # example pattern on lower bits
        copy_to_storage_register()               # update outputs
        time.sleep(2)

        reset_storage_register()       # clear all outputs again
        time.sleep(2)

except KeyboardInterrupt:
    pass

finally:
    GPIO.cleanup()                     # clean up GPIO pins when program stops