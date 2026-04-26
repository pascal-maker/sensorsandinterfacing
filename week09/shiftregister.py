import time #time.sleep()
import threading #threading.Thread
from queue import Queue, Empty

import  RPi.GPIO as GPIO #GPIO.setmode,GPIO.setup,GPIO.output,GPIO.cleanup

DS = 22#datapin
STCP = 27#latch
SHCP = 17#shift

class ShiftRegister:
    MSB_TO_LSB = "MSB TO LSB"#most significant bit to least significant bit
    LSB_TO_MSB = "LSB TO MSB"#least significant bit to most significant bit

    def __init__(self):
        GPIO.setmode(GPIO.BCM)#we are using the board pins
        GPIO.setwarnings(False)#we are ignoring any warnings

        GPIO.setup(DS, GPIO.OUT)#setting the pins as outputs
        GPIO.setup(STCP, GPIO.OUT)
        GPIO.setup(SHCP, GPIO.OUT)

        GPIO.output(DS, GPIO.LOW)#setting the pins to low
        GPIO.output(STCP, GPIO.LOW)
        GPIO.output(SHCP, GPIO.LOW)

    def pulse(self, pin):#pulse is a small burst of high voltage
        GPIO.output(pin, GPIO.HIGH)#we are setting the pin to high
        time.sleep(0.000001)#we are waiting for 0.000001 seconds
        GPIO.output(pin, GPIO.LOW)#we are setting the pin to low
        time.sleep(0.000001)#we are waiting for 0.000001 seconds

    def shift_byte_out(self,byte,direction=MSB_TO_LSB):#the function that shifts the byte out
        byte &= 0xFF #masking the byte to 8 bits
        if direction == self.MSB_TO_LSB:#if the direction is msb to lsb
          bit_range = range(7, -1, -1)#we are iterating from 7 to 0
        else:#if the direction is lsb to msb
          bit_range = range(8)#we are iterating from 0 to 7

        for i in bit_range:#for each bit in the range
          bit = (byte >> i) & 1#we are getting the bit
          GPIO.output(DS, bit)#we are setting the pin to high or low
          self.pulse(SHCP)#we are pulsing the shift clock

    def shift_out_16bit(self,value,direction=MSB_TO_LSB):#the function that shifts the 16 bit value out
        value &= 0xFFFF#masking the value to 16 bits
        msb = ( value >> 8) & 0xFF#getting the most significant bit
        lsb = value & 0xFF#getting the least significant bit

        self.shift_byte_out(msb,direction)#shifting out the most significant bit
        self.shift_byte_out(lsb,direction)#shifting out the least significant bit
        self.pulse(STCP)#pulsing the latch clock
    
    def clear(self):#clearing the shift register
        self.shift_out_16bit(0x0000)#setting the shift register to 0x0000
     