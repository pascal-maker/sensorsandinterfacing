#!/home/pi/venv/bin/python
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()

try:
    text = input("Enter text to write to card: ")
    print("Hold a card or tag near the reader...")
    reader.write(text)
    print("Written successfully!")
finally:
    GPIO.cleanup()
