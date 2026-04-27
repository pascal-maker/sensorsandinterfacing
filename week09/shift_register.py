import time
import RPi.GPIO as GPIO#import RPi.GPIO as GPIO so we can use its functions to control the shift register

DS = 22#data pin is used to send data to the shift register
STCP = 27#latch pin is used to latch the data to the shift register
SHCP = 17#clock pin is used to clock the data to the shift register

class ShiftRegister:#shift register class
    MSB_TO_LSB = "MSB_TO_LSB"#most significant bit to least significant bit
    LSB_TO_MSB = "LSB_TO_MSB"#least significant bit to most significant bit

    def __init__(self):#constructor
        self.ds = DS#data pin
        self.stcp = STCP#latch pin
        self.shcp = SHCP#clock pin

        for pin in (self.ds, self.stcp, self.shcp):#we set the pins to output and initial value to low
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)

    def pulse(self, pin):#this function pulses the pin
        GPIO.output(pin, GPIO.HIGH)#we set the pin to high
        time.sleep(0.000001)#we wait for 1 microsecond
        GPIO.output(pin, GPIO.LOW)#we set the pin to low
        time.sleep(0.000001)#we wait for 1 microsecond

    def shift_byte_out(self, byte, direction=MSB_TO_LSB):#this function shifts out a byte
        byte &= 0xFF#we mask the byte to 8 bits

        if direction == self.MSB_TO_LSB:#if the direction is most significant bit to least significant bit
            bit_range = range(7, -1, -1)#we set the bit range to 7 to -1 in steps of -1
        else:
            bit_range = range(8)#we set the bit range to 0 to 8 in steps of 1

        for i in bit_range:#we loop through each bit in the bit range
            GPIO.output(self.ds, (byte >> i) & 1)#we set the data pin to the value of the current bit
            self.pulse(self.shcp)#we pulse the clock pin

    def shift_out_16bit(self, value, direction=LSB_TO_MSB):#this function shifts out a 16-bit value
        value &= 0xFFFF#we mask the value to 16 bits

        msb = (value >> 8) & 0xFF#we get the most significant bit
        lsb = value & 0xFF#we get the least significant bit

        if direction == self.LSB_TO_MSB:#if the direction is least significant bit to most significant bit
            self.shift_byte_out(lsb, direction)#we shift out the least significant bit
            self.shift_byte_out(msb, direction)#we shift out the most significant bit
        else:
            self.shift_byte_out(msb, direction)#we shift out the most significant bit
            self.shift_byte_out(lsb, direction)#we shift out the least significant bit

        self.pulse(self.stcp)#we pulse the latch pin