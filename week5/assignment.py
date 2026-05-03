import RPi.GPIO as GPIO
import time
import smbus
import threading
import I2C_LCD_DRIVER

SERVO_PIN  = 18
BUTTON_PIN = 20

I2C_ADDR   = I2C_LCD_DRIVER.ADDRESS  # 0x27
LCD_WIDTH  = 16
LCD_CHR    = I2C_LCD_DRIVER.Rs       # character mode
LCD_CMD    = 0                        # command mode
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
ADC_ADDR   = 0x48

bus = smbus.SMBus(1)
lcd = I2C_LCD_DRIVER.lcd()

system_on = True
lock = threading.Lock()

GPIO.setwarnings(False) # Disables warning messages 
GPIO.setmode(GPIO.BCM)  # Sets the GPIO mode to BCM

GPIO.setup(SERVO_PIN, GPIO.OUT) #Initializes the servo pin as output
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) #Initializes the button pin as input 

servo = GPIO.PWM(SERVO_PIN, 50)#Initializing the servo 
servo.start(0)#Starts the servo

CMD_A4 = 0x44

def read_adc():
    bus.write_byte(ADC_ADDR, CMD_A4)
    bus.read_byte(ADC_ADDR)
    return bus.read_byte(ADC_ADDR)

def toggle_system():
    global system_on
    with lock:
        system_on = not system_on
    print("System ON" if system_on else "System OFF")

GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=toggle_system,bouncetime=200)     #Adds an event detect to the button pin 

try:#The try block is used to catch any errors that may occur
    while True:#The while loop runs indefinitely
        with lock:#Creates a lock to prevent race conditions
            active = system_on#Sets the active variable to the system_on variable
        if active:#If the active variable is true
            adc_val = read_adc()
            print("ADC Value: ",adc_val)#Prints the ADC value
            angle =  int((adc_val / 255) * 180)#Calculates the angle based on the ADC value
            duty = 2.5 + (angle /180 )*10 #Calculates the duty cycle based on the angle
            servo.ChangeDutyCycle(duty)#Changes the duty cycle of the servo

            line1 = f"ADC:{adc_val:3d}".ljust(LCD_WIDTH)
            line2 = f"Angle:{angle:3d}".ljust(LCD_WIDTH)
            lcd.lcd_display_string(line1, 1)
            lcd.lcd_display_string(line2, 2)

            print(f"ADC: {adc_val} Angle: {angle} ")#Prints the ADC value and angle
        else:
            servo.ChangeDutyCycle(0)  #Stops the servo
            lcd.lcd_display_string("System OFF".ljust(LCD_WIDTH), 1)
            lcd.lcd_display_string("".ljust(LCD_WIDTH), 2)
            print("System OFF")#Prints that the system is off
        time.sleep(0.1)    
except KeyboardInterrupt:#If the keyboard interrupt is called
    servo.stop()#Stops the servo
    GPIO.cleanup()#Cleans up the GPIO pins
    bus.close()#Closes the I2C bus
# LCD DISPLAY AND SERVO
# MULTIMEDIA AND CREATIVE TECHNOLOGY
# Assignment
# Create a program which can control the servo by turning 1 of the potentiometers (A4)
# The full range of the potentiometer controls the full range of the servo
# Show the current analog value of the potentiometer (0 – 255) on line 1 of the LCD
# Show the current angle of the servo on line 2 of the LCD
# Extra: use a button to be able to turn the system “on” and “off"