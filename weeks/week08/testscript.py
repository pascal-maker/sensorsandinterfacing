import RPi.GPIO as GPIO
import time

DATA = 22
CLOCK = 17
LATCH = 27

GPIO.setmode(GPIO.BCM)

GPIO.setup(DATA, GPIO.OUT)
GPIO.setup(CLOCK, GPIO.OUT)
GPIO.setup(LATCH, GPIO.OUT)

def write_bit(bit):

    GPIO.output(DATA, bit)

    GPIO.output(CLOCK, GPIO.HIGH)
    GPIO.output(CLOCK, GPIO.LOW)

def latch():

    GPIO.output(LATCH, GPIO.HIGH)
    GPIO.output(LATCH, GPIO.LOW)

def write_byte(value):

    for i in range(7, -1, -1):

        bit = (value >> i) & 1

        write_bit(bit)

try:

    while True:

        # all LEDs ON
        write_byte(0xFF)
        write_byte(0xFF)
        latch()

        print("ALL ON")

        time.sleep(2)

        # all LEDs OFF
        write_byte(0x00)
        write_byte(0x00)
        latch()

        print("ALL OFF")

        time.sleep(2)

except KeyboardInterrupt:

    GPIO.cleanup()