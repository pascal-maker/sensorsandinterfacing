import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
tx_pin = 17
BAUD_RATE = 9600
BIT_PERIOD = 1.0 / BAUD_RATE

GPIO.setup(tx_pin, GPIO.OUT, initial=GPIO.HIGH)

def send_byte(byte):
    GPIO.output(tx_pin, GPIO.LOW)       # start bit
    time.sleep(BIT_PERIOD)
    for i in range(8):                  # 8 data bits, LSB first
        GPIO.output(tx_pin, (byte >> i) & 1)
        time.sleep(BIT_PERIOD)
    GPIO.output(tx_pin, GPIO.HIGH)      # stop bit
    time.sleep(BIT_PERIOD)

def send_string(text):
    for char in text:
        send_byte(ord(char))

try:
    send_string("hello world")
except KeyboardInterrupt:
    print("Program stopped by user")
finally:
    GPIO.cleanup()
    print("GPIO cleaned up")
