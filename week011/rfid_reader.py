#!/home/pi/venv/bin/python
import time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522, MFRC522

GPIO.setmode(GPIO.BCM)
reader = SimpleMFRC522()
reader.READER = MFRC522(debugLevel='CRITICAL')

print("Hold a card or tag near the reader...")

try:
    while True:
        id, text = reader.read()
        print(f"ID:   {id}")
        print(f"Text: {text.strip()}")
        print("-" * 30)
        time.sleep(2)
finally:
    GPIO.cleanup()
