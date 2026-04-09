from RPi import GPIO
import time
GPIO.setmode(GPIO.BCM)
ledpin = 17
GPIO.setup(ledpin, GPIO.OUT)

def send_byte(byte):
    #foreach bit fo this byte , output the led with delay
    for bit_position in range(7,-1,-1):#looping through the bits of the byte from most significant to least significant you must start at bit 7 and go down to bit 0
        bit = (byte >> bit_position) & 1#getting the bit position using bitwise right shift and bitwise AND for example binary of 104 is 01101000 and bit_position = 7 byte >> 7 & 1 shift right by 7 and keep pnly the last bit 
        if bit == 1:#if the bit is 1
            GPIO.output(ledpin, GPIO.HIGH)#setting the led pin to high
        else:#if the bit is 0
            GPIO.output(ledpin, GPIO.LOW)#setting the led pin to low
        time.sleep(0.2)#waiting for 0.2 seconds delay between bits

try:
    def send_string(text):#function to send a string
        for char in text:#looping through the string parse character by character
            ascii_value = ord(char)#getting the ascii value of the character convert to 8-bit binary with ord character vcan become nuber taht is end by bits
            send_byte(ascii_value)#sending the byte
            time.sleep(1)#waiting for 1 second insert a delay between chracters
    send_string("hello")#setting the message to be sent send a message via a gpio pin
    print("Transmission complete")#printing that the transmission is complete
except KeyboardInterrupt:#if the transmission is interrupted
    print("Transmission interrupted")#printing that the transmission was interrupted
finally:
    GPIO.output(ledpin, GPIO.LOW)#setting the led pin to low
    GPIO.cleanup()#cleaning up the GPIO pins
