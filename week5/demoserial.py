import RPi.GPIO as GPIO#imports the RPi.GPIO library
import time#imports the time library

GPIO.setmode(GPIO.BCM) #sets the mode to BCM
tx_pin = 17 #sets the tx pin
BAUD_RATE = 9600 #sets the baud rate
BIT_PERIOD = 1.0 / BAUD_RATE#calculates the bit period

GPIO.setup(tx_pin, GPIO.OUT, initial=GPIO.HIGH) #sets the tx pin as output

def send_byte(byte): #sends a byte to the serial
    GPIO.output(tx_pin, GPIO.LOW)       # start bit
    time.sleep(BIT_PERIOD)#waits for the bit period
    for i in range(8):                  # 8 data bits, LSB first
        GPIO.output(tx_pin, (byte >> i) & 1) #outputs the byte
        time.sleep(BIT_PERIOD)#waits for the bit period
    GPIO.output(tx_pin, GPIO.HIGH)      # stop bit
    time.sleep(BIT_PERIOD)#waits for the bit period

def send_string(text): #sends a string to the serial
    for char in text:
        send_byte(ord(char))#sends the character to the serial

try:
    send_string("hello world")#sends the string "hello world" to the serial
except KeyboardInterrupt:
    print("Program stopped by user")#prints that the program was stopped by the user
finally:
    GPIO.cleanup()#cleans up the GPIO pins
    print("GPIO cleaned up")#prints that the GPIO pins were cleaned up
