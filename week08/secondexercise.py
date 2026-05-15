import RPi.GPIO as GPIO
import time


class ShiftRegister:
    def __init__(self, data_pin=22, clock_pin=17, latch_pin=27):# class for controlling the 74HC595 shift register
        self.data_pin = data_pin# serial data input
        self.clock_pin = clock_pin# shift clock
        self.latch_pin = latch_pin# storage/latch clock
        self._setup()

    def _setup(self):
        GPIO.setmode(GPIO.BCM)#BCM mode
        GPIO.setup(self.data_pin, GPIO.OUT)#seting up data pin as output
        GPIO.setup(self.clock_pin, GPIO.OUT)#seting up clock pin as output
        GPIO.setup(self.latch_pin, GPIO.OUT)#seting up latch pin as output

        GPIO.output(self.data_pin, 0)#seting data pin to low
        GPIO.output(self.clock_pin, 0)#seting clock pin to low
        GPIO.output(self.latch_pin, 0)#seting latch pin to low

    def write_one_bit(self, bit):#write one bit to the shift register
        GPIO.output(self.data_pin, GPIO.HIGH if bit else GPIO.LOW)#seting data pin to high or low depending on the bit
        GPIO.output(self.clock_pin, GPIO.HIGH)#pulse the clock pin
        GPIO.output(self.clock_pin, GPIO.LOW)#pulse the clock pin

    def storage_pulse(self):#pulse the storage/latch pin
        GPIO.output(self.latch_pin, GPIO.HIGH)#pulse the latch pin
        GPIO.output(self.latch_pin, GPIO.LOW)#pulse the latch pin

    def write_byte(self, data_byte):#write one byte to the shift register
        mask = 0b10000000#mask to get the most significant bit
        for _ in range(8):#loop through the 8 bits
            bit = (data_byte & mask) != 0#check if the most significant bit is 1
            self.write_one_bit(bit)#write the bit to the shift register
            mask >>= 1#shift the mask to the right

    def shift_out_16bit(self, value):#write 16 bits to the shift register
        high_byte = (value >> 8) & 0xFF#get the most significant byte
        low_byte = value & 0xFF#get the least significant byte

        self.write_byte(high_byte)#write the most significant byte to the shift register
        self.write_byte(low_byte)#write the least significant byte to the shift register
        self.storage_pulse()#pulse the storage/latch pin

    def clear(self):#clear the shift register by sending out 16 bits that are all 0
        self.shift_out_16bit(0)#write 0 to the shift register


class LedBarGraph:# class for controlling the LED bar graph
    def __init__(self, shift_register):#initializes the LED bar graph with the shift register
        self.shift_register = shift_register#

    def set_pattern(self, value, fill=False):#set the pattern of the LED bar graph
        if value < 0:#if the value is less than 0
            value = 0
        if value > 10:#if the value is greater than 10
            value = 10

        if value == 0:#if the value is 0
            pattern = 0#pattern is 0
        elif fill:#if the fill mode is enabled
            pattern = (1 << value) - 1#pattern is 2 to the power of the value minus 1 for example we have the number 4 in binary it is 0b100 so if we want to fill it we need to make it 0b111 which is 7 so we do 2 to the power of 4 minus 1 which is 16 minus 1 which is 15 when we fill into leds we then have all the leds on up to the number we want so it will light up the first 4 leds 2. Fill mode
#pattern = (1 << value) - 1

#This is the interesting part.

#Suppose:

#value = 4

#First:

#1 << 4

#means:

#0000000001

#shift left 4 times:

#0000010000

#which equals:

#16

#Then:

#16 - 1

#gives:

#15

#Binary 15 is:

#0000001111

#So the first 4 LEDs turn ON
        #else: #if the fill mode is not enabled
        pattern = 1 << (value - 1)#pattern is 2 to the power of the value minus 1

        self.shift_register.shift_out_16bit(pattern)#write the pattern to the shift register

    def clear(self):#clear the shift register by sending out 16 bits that are all 0
        self.shift_register.clear()#write 0 to the shift register


if __name__ == "__main__":
    try:
        shift_reg = ShiftRegister()#create shift register
        led_bar = LedBarGraph(shift_reg)#create led bar graph

        while True:#loop forever
            number = int(input("Number 0-10: "))#get number from user
            fill_text = input("Fill? (y/n): ").strip().lower()
            fill = fill_text == "y"

            led_bar.set_pattern(number, fill)#set the pattern of the LED bar graph

    except KeyboardInterrupt:
        pass
    finally:#cleanup the GPIO pins when the program is exited
        GPIO.cleanup()