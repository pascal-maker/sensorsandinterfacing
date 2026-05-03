import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
led_pin = 17  # blue LED = TX pin
GPIO.setup(led_pin, GPIO.OUT)

def send_byte(byte):
    for bit_position in range(7, -1, -1):   # MSB first
        bit = (byte >> bit_position) & 1
        GPIO.output(led_pin, bit)
        time.sleep(0.2)                     # 200ms per bit

def send_string(text):
    for char in text:
        send_byte(ord(char))                # convert character to ASCII
        time.sleep(1)                       # 1 second between characters

try:
    send_string("hello world")
except KeyboardInterrupt:
    print("Program stopped by user")
finally:
    GPIO.cleanup()
    print("GPIO cleaned up")
