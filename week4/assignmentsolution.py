

import RPi.GPIO as GPIO
import smbus
import time

# --------------------------------------------------
# I2C / ADS7830 setup
# --------------------------------------------------

# Use I2C bus 1 on the Raspberry Pi
I2C_BUS = 1

# I2C address of the ADS7830 ADC chip
ADS7830_ADDR = 0x48

# Open the I2C bus so Python can talk to the ADC
bus = smbus.SMBus(I2C_BUS)

# ADS7830 command bytes for the channels we want to read
# A2 -> channel 2
# A3 -> channel 3
# A4 -> channel 4
CMD_A2 = 0x94
CMD_A3 = 0xD4
CMD_A4 = 0xA4

# Reference voltage used to convert ADC value back into volts
# The assignment says convert to 0V - 5V
VREF = 5.0


# --------------------------------------------------
# RGB LED setup
# --------------------------------------------------
# Freenove RGB module is connected to:
# Red   -> GPIO5
# Green -> GPIO6
# Blue  -> GPIO13
#
# Note:
# This board uses a Common Anode RGB LED, so the logic is inverted:
# lower duty cycle = brighter
# higher duty cycle = more off
# --------------------------------------------------

R_PIN = 5
G_PIN = 6
B_PIN = 13


# --------------------------------------------------
# Button setup
# --------------------------------------------------
# We use 1 button to toggle the system on/off.
# Change this pin if your chosen board button uses another GPIO.
# --------------------------------------------------

BUTTON_PIN = 20


# --------------------------------------------------
# GPIO mode and pin configuration
# --------------------------------------------------

# Use BCM numbering for GPIO pins
GPIO.setmode(GPIO.BCM)

# Set RGB pins as outputs
GPIO.setup(R_PIN, GPIO.OUT)
GPIO.setup(G_PIN, GPIO.OUT)
GPIO.setup(B_PIN, GPIO.OUT)

# Set button pin as input with pull-up resistor
# Pull-up means:
# - normal state = HIGH (1)
# - pressed      = LOW  (0)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# --------------------------------------------------
# Create PWM objects for the RGB pins
# --------------------------------------------------
# Frequency = 1000 Hz
# --------------------------------------------------

pwm_r = GPIO.PWM(R_PIN, 1000)
pwm_g = GPIO.PWM(G_PIN, 1000)
pwm_b = GPIO.PWM(B_PIN, 1000)

# Start PWM signals with 100% duty cycle
# Because the LED is Common Anode, 100% means "most off"
# (though it may not become perfectly off because of the 5V board wiring)
pwm_r.start(100)
pwm_g.start(100)
pwm_b.start(100)


# --------------------------------------------------
# System state
# --------------------------------------------------
# True  = RGB system active
# False = RGB system off-ish
# --------------------------------------------------

system_on = True


# --------------------------------------------------
# Function: read ADS7830 channel
# --------------------------------------------------
# Sends a command byte to the ADC and reads back one 8-bit value.
# Also converts the raw ADC value (0..255) back into volts.
# --------------------------------------------------

def read_ads7830(command):
    # Send the command byte to the ADC
    bus.write_byte(ADS7830_ADDR, command)

    # Read back 1 byte from the ADC (0..255)
    value = bus.read_byte(ADS7830_ADDR)

    # Convert raw ADC value into voltage
    voltage = value * VREF / 255

    # Return both the raw value and the converted voltage
    return value, voltage


# --------------------------------------------------
# Function: convert ADC value to inverted PWM duty cycle
# --------------------------------------------------
# ADC gives 0..255
# PWM duty cycle needs 0..100
#
# Normally:
# - higher value = brighter
#
# But because the LED is Common Anode:
# - lower duty cycle = brighter
# - higher duty cycle = darker / off-ish
#
# So we first map 0..255 -> 0..100,
# then invert it.
# --------------------------------------------------
# --------------------------------------------------
# Button callback function
# --------------------------------------------------
# This function runs automatically whenever the button is pressed.
# It toggles the system state between ON and OFF.
# --------------------------------------------------

def adc_to_inverted_duty(adc_value):
    brightness = adc_value * 100 / 255
    duty = 100 - brightness
    return duty

def toggle_system(channel):
    global system_on
    system_on = not system_on
    if system_on:
        print("System turned ON")
    else:
        print("System turned OFF")



# --------------------------------------------------
# Add button event detection
# --------------------------------------------------
# We detect a falling edge because:
# - pull-up button is normally HIGH
# - when pressed it goes LOW
#
# bouncetime helps debounce the button.
# -----------------------------------------------


GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=toggle_system, bouncetime=200)  



# --------------------------------------------------
# Main program loop
# -      

try:
    while True:
        if system_on:
            adc_r,volt_r = read_ads7830(CMD_A2)
            adc_g,volt_g = read_ads7830(CMD_A3)
            adc_b,volt_b = read_ads7830(CMD_A4)
            
            duty_r = adc_to_inverted_duty(adc_r)
            duty_g = adc_to_inverted_duty(adc_g)
            duty_b = adc_to_inverted_duty(adc_b)
            pwm_r.ChangeDutyCycle(duty_r)
            pwm_g.ChangeDutyCycle(duty_g)
            pwm_b.ChangeDutyCycle(duty_b) 
            
            print(f"R: {adc_r:3d} ({volt_r:.2f} V) ")
            print(f"G: {adc_g:3d} ({volt_g:.2f} V)")
            print(f"B: {adc_b:3d} ({volt_b:.2f} V) ")    
        else:
            # System is OFF, set RGB to off-ish state
            pwm_r.ChangeDutyCycle(100)
            pwm_g.ChangeDutyCycle(100)
            pwm_b.ChangeDutyCycle(100)   
        time.sleep(0.1)  # Small delay to avoid busy looping
except KeyboardInterrupt:     
   GPIO.remove_event_detect(BUTTON_PIN)  # Clean up button event detection
   pwm_r.stop()
   pwm_g.stop() 
   pwm_b.stop() 
   
   bus.close()
   GPIO.cleanup()