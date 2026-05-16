# ----------------------------------------
# IMPORTS
# ----------------------------------------

import RPi.GPIO as GPIO#library to control Raspberry Pi GPIO pins
import smbus2#library to control Raspberry Pi I2C pins
import time#library to control Raspberry Pi time

# ----------------------------------------
# GPIO CONSTANTS
# ----------------------------------------

BUTTON = 20          # Button GPIO
BUZZER = 12          # Passive buzzer GPIO

# Shift register pins
DATA_PIN = 22        # DS
CLOCK_PIN = 17       # SHCP
LATCH_PIN = 27       # STCP

# ----------------------------------------
# ADC SETUP
# ----------------------------------------

I2C_ADDRESS = 0x48 # Address of the ADC
bus = smbus2.SMBus(1) # Open I2C bus

# ADS7830 command table
COMMANDS = [
    0x84,  # CH0
    0xC4,  # CH1
    0x94,  # CH2 -> A2
    0xD4,  # CH3 -> A3
    0xA4,  # CH4 -> A4
    0xE4,  # CH5
    0xB4,  # CH6
    0xF4   # CH7
]

# Potentiometer channel
A2_CHANNEL = 2#

# ----------------------------------------
# GPIO SETUP
# ----------------------------------------

GPIO.setmode(GPIO.BCM)#set up GPIO mode

GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)#set up button as input with pull up resistor

GPIO.setup(DATA_PIN, GPIO.OUT)#set up data pin as output
GPIO.setup(CLOCK_PIN, GPIO.OUT)#set up clock pin as output
GPIO.setup(LATCH_PIN, GPIO.OUT)#set up latch pin as output

GPIO.setup(BUZZER, GPIO.OUT)#set up buzzer as output

# ----------------------------------------
# BUZZER PWM
# ----------------------------------------

buzzer_pwm = GPIO.PWM(BUZZER, 100)#set up buzzer PWM
buzzer_pwm.start(50)#start buzzer PWM with 50% duty cycle

# ----------------------------------------
# GLOBAL VARIABLES
# ----------------------------------------

fill_mode = False#set default fill mode to False

# ----------------------------------------
# BUTTON INTERRUPT
# ----------------------------------------

def toggle_fill(channel):#toggle fill mode when button is pressed

    global fill_mode#declare global variable

    fill_mode = not fill_mode#toggle fill mode

    print("Fill mode:", fill_mode)#print fill mode

GPIO.add_event_detect(  #set up event detection for the button
    BUTTON,# GPIO pin
    GPIO.FALLING,#event type
    callback=toggle_fill,#function to call when event is detected
    bouncetime=300#time to wait before detecting another event
)

# ----------------------------------------
# READ ADC
# ----------------------------------------

def read_channel(channel):#read ADC value

    command = COMMANDS[channel]#get command for channel

    bus.write_byte(I2C_ADDRESS, command)#write command to ADC

    return bus.read_byte(I2C_ADDRESS)#read ADC value

# ----------------------------------------
# SHIFT REGISTER FUNCTIONS
# ----------------------------------------

def write_one_bit(bit):#write one bit to shift register

    GPIO.output(DATA_PIN, bit)#set data pin to bit

    GPIO.output(CLOCK_PIN, GPIO.HIGH)#set clock pin to high
    GPIO.output(CLOCK_PIN, GPIO.LOW)#set clock pin to low

def copy_to_storage_register():#copy data to storage register

    GPIO.output(LATCH_PIN, GPIO.HIGH)#set latch pin to high
    GPIO.output(LATCH_PIN, GPIO.LOW)#set latch pin to low

def write_byte(value):#write byte to shift register

    for i in range(7, -1, -1):#loop through bits of value

        bit = (value >> i) & 1#get bit

        write_one_bit(bit)#write bit

def shift_out_16bit(value):#shift out 16 bit value to shift register

    high_byte = (value >> 8) & 0xFF#get high byte
    low_byte = value & 0xFF#get low byte

    write_byte(high_byte)#write high byte
    write_byte(low_byte)#write low byte

    copy_to_storage_register()#copy data to storage register

def clear_register():#clear shift register

    shift_out_16bit(0)#shift out 16 bit value 0 to shift register

# ----------------------------------------
# CREATE LED PATTERN
# ----------------------------------------

def set_bar_graph(value, fill=False):#set bar graph pattern

    # Keep value between 0 and 10
    if value < 0:#if value is less than 0
        value = 0

    if value > 10:#if value is greater than 10
        value = 10

    # All LEDs OFF
    if value == 0:#if value is 0

        pattern = 0#set pattern to 0

    # Fill mode
    elif fill:#if fill mode is enabled

        pattern = (1 << value) - 1#set pattern to fill mode for exmaple value is 4 (binary 100) then shift left 4 times (1000000) and subtract 1 (1111111) so first 4 LEDs are on
        

    # Single LED mode
    else:

        pattern = 1 << (value - 1)#set pattern to single LED mode for exmaple value is 4 then 4-1 is 3 then 1<<3 is 8 (binary 100) so 4th LED is on

    shift_out_16bit(pattern)#shift out 16 bit value to shift register

# ----------------------------------------
# MAIN LOOP
# ----------------------------------------

try:#try block to catch errors

    while True:#loop indefinitely

        # Read potentiometer
        analog_value = read_channel(A2_CHANNEL)#read ADC value

        # Scale 0-255 -> 0-10
        led_value = int((analog_value / 255) * 10)#scale ADC value to 0-10

        # Show LEDs
        set_bar_graph(led_value, fill_mode)#set bar graph pattern

        # Convert potentiometer to frequency
        frequency = 100 + int((analog_value / 255) * 1000)#convert ADC value to frequency

        # Change buzzer frequency
        buzzer_pwm.ChangeFrequency(frequency)#change buzzer frequency

        # Debug output
        print(
            f"ADC={analog_value} "#print ADC value
            f"LED={led_value} "#print LED value
            f"Freq={frequency}Hz "#print frequency
            f"Fill={fill_mode}"#print fill mode
        )

        time.sleep(0.05)#wait for 0.05 seconds

# ----------------------------------------
# EXIT CLEANLY
# ----------------------------------------

except KeyboardInterrupt: #catch keyboard interrupt error

    pass

finally: #finally block to clean up

    buzzer_pwm.stop() #stop buzzer PWM

    clear_register()#clear shift register

    GPIO.cleanup()#cleanup GPIO pins

    bus.close()#close I2C bus