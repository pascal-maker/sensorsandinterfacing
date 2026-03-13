import RPi.GPIO as GPIO
import time

LED_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.output(LED_PIN, GPIO.LOW)

def send_byte(char):
    ascii_value = ord(char)
    print(f"Sending character: '{char}")
    print(f"ASCII value: {ascii_value}")
    print(f"Binary value: {ascii_value:08b}")
    
    
    for i in range(7, -1, -1):
        bit = (ascii_value >> i) & 1
        print(bit,end="",flush=True)
        if bit == 1:
            GPIO.output(LED_PIN, GPIO.HIGH)
        else:
            GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(0.2)
    print()
    
    GPIO.output(LED_PIN, GPIO.LOW)
    
def send_message(message):
    for char in message:
        send_byte(char)
        time.sleep(1)
        
try:
    message = "Hello"
    print("Starting transmission...\n")     
    
    send_message(message)
    print("\nTransmission complete.")
except KeyboardInterrupt:
    print("\nTransmission interrupted.")
except KeyboardInterrupt:
    print("\n Program stopped by user.")
finally:
   GPIO.output(LED_PIN, GPIO.LOW)
   GPIO.cleanup()
    
    
#In this exercise I used the blue LED as a transmitting pin.
#The program converts each character of the message into its ASCII value using ord().
#hen it sends the byte bit by bit, starting with the most significant bit.
#A bit value of 1 turns the LED on and a bit value of 0 turns the LED off.
#There is a delay of 200 ms between bits and 1 second between characters.
#In this way the text "hello" is transmitted as a light signal.   