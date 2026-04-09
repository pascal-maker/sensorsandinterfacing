import RPi.GPIO as GPIO#importing the GPIO library
import time#importing the time library

LED_TX = 17#setting the LED pin to 17 . “Use our blue LED as TX pin”

GPIO.setmode(GPIO.BCM)#setting the mode to BCM
GPIO.setup(LED_TX, GPIO.OUT)#setting the LED pin to output Because tranmission means: HIGH = send a 1 LOW = send a 0
GPIO.output(LED_TX, GPIO.LOW)#setting the LED pin to low

def send_byte(byte): #function to send a byte function that takes an integer (0–255) and flashes the LED for each bit one character a time as 8 bits
  for bit_position in range(7,-1,-1):#looping through the bits of the byte from most significant to least significant you must start at bit 7 and go down to bit 0
    bit = (byte >> bit_position) & 1#getting the bit position using bitwise right shift and bitwise AND for example binary of 104 is 01101000 and bit_position = 7 byte >> 7 & 1 shift right by 7 and keep pnly the last bit 
    print(bit, end="", flush=True)#printing the bit print 1 or 0 to the console 
    if bit == 1:#if the bit is 1
      GPIO.output(LED_TX, GPIO.HIGH)#setting the LED pin to high
    else:#if the bit is 0 gpio led off and led on actual light signal
      GPIO.output(LED_TX, GPIO.LOW)#setting the LED pin to low
    time.sleep(0.2)#waiting for 0.2 seconds delay between bits 
 


try:
  message = "Hello"#setting the message to be sent send a message via a gpio pin
  for c in message:#looping through the message parse character by character
    ascii_value = ord(c)#getting the ascii value of the character convert to 8-bit binary with ord character vcan become nuber taht is end by bits
    print(f"Sending '{c}' -> {ascii_value} -> {ascii_value:08b}")#printing the character, ascii value, and binary value
    send_byte(ascii_value)#sending the byte
    time.sleep(1)#waiting for 1 second insert a delay between chracters 

  print("\nTransmission complete.")#printing that the transmission is complete
except KeyboardInterrupt:#if the transmission is interrupted
  print("\nTransmission interrupted.")#printing that the transmission was interrupted
finally:
  GPIO.output(LED_TX, GPIO.LOW)#setting the LED pin to low
  GPIO.cleanup()#cleaning up the GPIO pins


#  ssignment → code
#blue LED = TX pin
#message = "hello"
#for c in message: = go through each character
#ord(c) = convert character to ASCII
#send_byte() = send 8 bits
#for bit_position in range(7, -1, -1) = MSB first
#(byte >> bit_position) & 1 = get one bit
#GPIO.HIGH / LOW = LED sends 1 or 0
#time.sleep(0.2) = 200 ms between bits
#time.sleep(1) = 1 second between characters