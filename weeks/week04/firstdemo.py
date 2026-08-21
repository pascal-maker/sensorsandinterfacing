"""
Week 4 — PWM & ADC
Classes:
- PWMLed
- ADS7830
- RGBLed
"""

import RPi.GPIO as GPIO#import RPi.GPIO library
import smbus#import smbus library
import time#import time library


# ============================================================================
# GPIO SETUP
# ============================================================================

GPIO.setmode(GPIO.BCM)#set the gpio mode

BTN_PIN = 20#set the button pin

GPIO.setup(BTN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)#set the button pin as input with pull-up


# ============================================================================
# PWM LED CLASS
# ============================================================================

class PWMLed:#class for pwm led

    def __init__(self, pin, frequency=1000):#initialize the led

        self.pin = pin#set the pin
        self.frequency = frequency#set the frequency

        GPIO.setup(self.pin, GPIO.OUT)#set the pin as output

        self.pwm = GPIO.PWM(self.pin, self.frequency)#create the pwm instance
        self.pwm.start(0)#start the pwm

    def set_brightness(self, percent):#sets the brightness of the led

        percent = max(0, min(100, percent))#set the brightness to be between 0 and 100

        self.pwm.ChangeDutyCycle(percent)#change the duty cycle of the pwm

    def stop(self):#stops the pwm   

        self.pwm.stop()#stops the pwm


# ============================================================================
# ADS7830 ADC CLASS
# ============================================================================

class ADS7830:#class for adc

    CHANNEL_COMMANDS = {
        0: 0x84,
        1: 0xC4,
        2: 0x94,
        3: 0xD4,
        4: 0xA4,
        5: 0xE4,
        6: 0xB4,
        7: 0xF4,
    }

    def __init__(self, address=0x48, bus_num=1, vref=5.0):#initialize the adc

        self.address = address#set the address
        self.vref = vref#set the voltage reference

        self.bus = smbus.SMBus(bus_num)#set the bus

    def read_raw(self, channel):#reads the raw value from the adc

        if channel not in self.CHANNEL_COMMANDS:#check if the channel is valid
            raise ValueError("Invalid ADC channel")#raise an error if the channel is invalid

        command = self.CHANNEL_COMMANDS[channel]#set the command for the channel

        self.bus.write_byte(self.address, command)#write the command to the ADC

        value = self.bus.read_byte(self.address)#read the ADC value

        return value#return the ADC value

    def read_voltage(self, channel):#reads the voltage from the adc

        raw = self.read_raw(channel)#read the raw value from the adc

        voltage = raw * self.vref / 255#calculate the voltage

        return voltage#return the voltage

    def close(self):#closes the bus 

        self.bus.close()#close the bus


# ============================================================================
# RGB LED CLASS
# ============================================================================

class RGBLed:#  class for rgb led

    def __init__(self, pin_r, pin_g, pin_b, frequency=1000):#initialize the rgb led

        self.pin_r = pin_r#set the pin for the red led
        self.pin_g = pin_g#set the pin for the green led
        self.pin_b = pin_b#set the pin for the blue led

        GPIO.setup(self.pin_r, GPIO.OUT)#set the pin as output
        GPIO.setup(self.pin_g, GPIO.OUT)#set the pin as output
        GPIO.setup(self.pin_b, GPIO.OUT)#set the pin as output

        self.red_pwm = GPIO.PWM(self.pin_r, frequency)#create the pwm instance
        self.green_pwm = GPIO.PWM(self.pin_g, frequency)#create the pwm instance
        self.blue_pwm = GPIO.PWM(self.pin_b, frequency)#create the pwm instance

        self.red_pwm.start(100)#start the pwm
        self.green_pwm.start(100)#start the pwm
        self.blue_pwm.start(100)#start the pwm

    def set_color(self, r, g, b):#sets the color of the led

        red_dc = 100 - (r * 100 / 255)#calculate the duty cycle for the red led
        green_dc = 100 - (g * 100 / 255)#calculate the duty cycle for the green led
        blue_dc = 100 - (b * 100 / 255)#calculate the duty cycle for the blue led

        self.red_pwm.ChangeDutyCycle(red_dc)#change the duty cycle of the red led
        self.green_pwm.ChangeDutyCycle(green_dc)#change the duty cycle of the green led
        self.blue_pwm.ChangeDutyCycle(blue_dc)#change the duty cycle of the blue led

    def off(self):#turns off the rgb led

        self.red_pwm.ChangeDutyCycle(100)#turn off the red led
        self.green_pwm.ChangeDutyCycle(100)#turn off the green led
        self.blue_pwm.ChangeDutyCycle(100)#turn off the blue led

    def stop(self):#stops the pwm

        self.red_pwm.stop()#stop the pwm
        self.green_pwm.stop()#stop the pwm
        self.blue_pwm.stop()#stop the pwm


# ============================================================================
# OBJECT CREATION
# ============================================================================

adc = ADS7830()#create the adc object 

rgb = RGBLed(
    pin_r=5,#set the pin for the red led
    pin_g=6,#set the pin for the green led
    pin_b=13#set the pin for the blue led
)

system_on = True


# ============================================================================
# BUTTON CALLBACK
# ============================================================================

def toggle_system(channel):#callback function for the button

    global system_on#global variable for the button 

    system_on = not system_on#toggle the system on and off

    if system_on:#if the system is on
        print("System ON")#print that the system is on
    else:
        print("System OFF")#print that the system is off


GPIO.add_event_detect(
    BTN_PIN,#set the button pin
    GPIO.FALLING,#set the button to detect falling edge
    callback=toggle_system,#set the callback function
    bouncetime=200#set the bouncetime
)


# ============================================================================
# MAIN LOOP
# ============================================================================

try:

    while True:#infinite loop to keep the program running

        if system_on:#if the system is on

            red_value = adc.read_raw(2)#read the red value
            green_value = adc.read_raw(3)#read the green value
            blue_value = adc.read_raw(4)#read the blue value

            rgb.set_color(
                red_value,#set the red value
                green_value,#set the green value
                blue_value#set the blue value
            )

            print(
                f"R:{red_value} "
                f"G:{green_value} "
                f"B:{blue_value}"
            )

        else:#if the system is off

            rgb.off()#turn off the rgb led

        time.sleep(0.1)#wait for 0.1 seconds

except KeyboardInterrupt:#if the user presses ctrl+c

    print("Program stopped")#print that the program has stopped

finally:

    GPIO.remove_event_detect(BTN_PIN)#remove the event detect

    rgb.stop()#stop the pwm

    adc.close()#close the adc

    GPIO.cleanup()#cleanup the gpio