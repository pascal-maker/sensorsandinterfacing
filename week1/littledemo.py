from RPi import GPIO
GPIO.setmode(GPIO.BCM)

GPIO.setup(9,GPIO.IN)
GPIO.setup((10,11,12)