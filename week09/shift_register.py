import time
import RPi.GPIO as GPIO


DS = 22
STCP = 27
SHCP = 17


class ShiftRegister:
    MSB_TO_LSB = "MSB_TO_LSB"
    LSB_TO_MSB = "LSB_TO_MSB"

    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(DS, GPIO.OUT)
        GPIO.setup(STCP, GPIO.OUT)
        GPIO.setup(SHCP, GPIO.OUT)

        GPIO.output(DS, GPIO.LOW)
        GPIO.output(STCP, GPIO.LOW)
        GPIO.output(SHCP, GPIO.LOW)

    def pulse(self, pin):
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(0.000001)
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.000001)

    def shift_byte_out(self, byte, direction=MSB_TO_LSB):
        byte &= 0xFF

        if direction == self.MSB_TO_LSB:
            bit_range = range(7, -1, -1)
        else:
            bit_range = range(8)

        for i in bit_range:
            bit = (byte >> i) & 1
            GPIO.output(DS, GPIO.HIGH if bit else GPIO.LOW)
            self.pulse(SHCP)

    def shift_out_16bit(self, value, direction=MSB_TO_LSB):
        value &= 0xFFFF

        msb = (value >> 8) & 0xFF
        lsb = value & 0xFF

        if direction == self.LSB_TO_MSB:
            self.shift_byte_out(lsb, direction)
            self.shift_byte_out(msb, direction)
        else:
            self.shift_byte_out(msb, direction)
            self.shift_byte_out(lsb, direction)

        self.pulse(STCP)