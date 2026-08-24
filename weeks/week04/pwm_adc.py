"""
Week 4 — PWM & ADC
Classes: PWMLed, ADS7830, RGBLed
"""

import RPi.GPIO as GPIO#import RPi.GPIO library
import smbus#import smbus library
import time#import time library


# The common-anode RGB LED is completely off at 100% duty cycle. Limiting the
# duty cycle to 95% keeps it faintly illuminated, as required by the assignment.
MAX_DUTY = 95


class PWMLed:
    """Single LED controlled via PWM (0–100 % brightness)."""

    def __init__(self, pin, frequency=1000):#initialize the LED
        GPIO.setup(pin, GPIO.OUT)#set the pin as output
        self._pwm = GPIO.PWM(pin, frequency)#create the PWM instance
        self._pwm.start(0)#start the PWM

    def set_brightness(self, percent):#sets the brightness of the LED
        """Set brightness 0–100 %."""
        percent = max(0, min(100, percent))#set the brightness to be between 0 and 100
        self._pwm.ChangeDutyCycle(percent)#change the duty cycle of the PWM

    def stop(self):#stops the PWM
        self._pwm.stop()#stops the pwm


class ADS7830:
    """
    Driver for the ADS7830 8-channel, 8-bit ADC over I2C.
    Default I2C address: 0x48.
    VREF: 3.3 V.
    """

    _CHANNEL_COMMANDS = {
        0: 0x84, 1: 0xC4,#the commands for the ADC chip to read the voltage from the pots
        2: 0x94, 3: 0xD4,#the commands for the ADC chip to read the voltage from the pots
        4: 0xA4, 5: 0xE4,#the commands for the ADC chip to read the voltage from the pots
        6: 0xB4, 7: 0xF4,#the commands for the ADC chip to read the voltage from the pots
    }

    def __init__(self, address=0x48, bus_num=1, vref=3.3):#initialize the ADC
        self.address = address#set the i2c address
        self.vref = vref#set the reference voltage
        self._bus = smbus.SMBus(bus_num)#set the i2c bus

    def read_raw(self, channel):#function to read the raw value from the ADC
        """Return raw ADC value (0–255) for the given channel."""
        if channel not in self._CHANNEL_COMMANDS:#check if the channel is valid
            raise ValueError(f"Invalid channel {channel}. Choose 0–7.")#raise an error if the channel is invalid
        cmd = self._CHANNEL_COMMANDS[channel]#set the command for the ADC chip to read the voltage from the pot
        self._bus.write_byte(self.address, cmd)#write the command to the ADC
        self._bus.read_byte(self.address)#discard the result from the previous conversion
        return self._bus.read_byte(self.address)#read the current adc value in the 0-255 range

    def read_voltage(self, channel):#function to read the voltage from the ADC
        """Return voltage in volts for the given channel."""
        return self.read_raw(channel) * self.vref / 255#read the voltage from the ADC

    def close(self):#function to close the ADC
        self._bus.close()#close the ADC


class RGBLed:
    """
    Common-anode RGB LED driven by three PWM channels.
    Because it's common-anode, lower duty cycle = brighter.
    """

    def __init__(self, pin_r, pin_g, pin_b, frequency=1000):#initialize the LED
        for pin in (pin_r, pin_g, pin_b):#set the pins as output
            GPIO.setup(pin, GPIO.OUT)#set the pin as output
        self._r = GPIO.PWM(pin_r, frequency)#create the PWM instance for the red led
        self._g = GPIO.PWM(pin_g, frequency)#create the PWM instance for the green led
        self._b = GPIO.PWM(pin_b, frequency)#create the PWM instance for the blue led
        self._r.start(MAX_DUTY)#start the red led with a faint glow
        self._g.start(MAX_DUTY)#start the green led with a faint glow
        self._b.start(MAX_DUTY)#start the blue led with a faint glow

    def set_color(self, r, g, b):#sets the color of the LED
        """
        Set color using 0–255 values per channel.
        Inverts to duty cycle for common-anode wiring.
        """
        self._r.ChangeDutyCycle(min(100 - r * 100 / 255, MAX_DUTY))#change the duty cycle of the red led
        self._g.ChangeDutyCycle(min(100 - g * 100 / 255, MAX_DUTY))#change the duty cycle of the green led
        self._b.ChangeDutyCycle(min(100 - b * 100 / 255, MAX_DUTY))#change the duty cycle of the blue led

    def off(self):#puts the LED in its faint-glow system-off state
        self._r.ChangeDutyCycle(MAX_DUTY)#keep the red led faintly lit
        self._g.ChangeDutyCycle(MAX_DUTY)#keep the green led faintly lit
        self._b.ChangeDutyCycle(MAX_DUTY)#keep the blue led faintly lit

    def stop(self):#stops the PWM
        self._r.stop()
        self._g.stop()
        self._b.stop()


# ---------------------------------------------------------------------------
# Demo — mirrors week4/assignmentsolution.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)#set the GPIO mode

    adc = ADS7830()#create the ADC instance
    rgb = RGBLed(pin_r=5, pin_g=6, pin_b=13)#create the RGB LED instance
    system_on = True#set the system state to on

    btn_pin = 20#set the button pin
    GPIO.setup(btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)#set the button pin as input with pull-up

    def toggle(channel):#function to toggle the system state
        global system_on#set the system state to on 
        system_on = not system_on#toggle the system state
        print("System ON" if system_on else "System OFF")#print the system state

    GPIO.add_event_detect(btn_pin, GPIO.FALLING, callback=toggle, bouncetime=200)#add an event detect to the button pin to call the toggle function when the button is pressed

    try:
        while True:
            if system_on:#if the system is on
                r = adc.read_raw(2)#read the red led value
                g = adc.read_raw(3)#read the green led value
                b = adc.read_raw(4)#read the blue led value
                rgb.set_color(r, g, b)#set the color of the led
                print(f"R:{r}  G:{g}  B:{b}")#print the led values
            else:
                rgb.off()#turns the led off
            time.sleep(0.1)#waits for 0.1 seconds
    except KeyboardInterrupt:
        pass
    finally:
        GPIO.remove_event_detect(btn_pin)#removes the event detect
        rgb.stop()#stops the pwm
        adc.close()#closes the adc
        GPIO.cleanup()#cleans up the GPIO pins
