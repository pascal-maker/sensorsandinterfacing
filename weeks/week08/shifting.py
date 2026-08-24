import RPi.GPIO as GPIO# library to control Raspberry Pi GPIO pins
import smbus2#library to control Raspberry Pi GPIO pins
import time#library to control Raspberry Pi GPIO pins

# -----------------------------
# Buttons
# -----------------------------
BUTTON_1 = 20#Button GPIO 20
BUTTON_2 = 16#Button GPIO 16
BUTTON_3 = 21#Button GPIO 21
BUTTON_4 = 26#Button GPIO 26

# -----------------------------
# Joystick ADC channels
# -----------------------------
X_JOYSTICK = 0#channel 0 for x-axis
Y_JOYSTICK = 1#channel 1 for y-axis

chip = 0x48#I2C address for ADC
bus = smbus2.SMBus(1)#I2C bus 1

# -----------------------------
# Read ADC
# -----------------------------
def read_channel(channel):#PCF8591: send control byte (0x40 | channel) then read one byte (0-255)
    bus.write_byte(chip, 0x40 | (channel & 0x03))#PCF8591: send control byte (0x40 | channel) then read one byte (0-255)
    bus.read_byte(chip)       # dummy read
    raw = bus.read_byte(chip)#PCF8591: read one byte (0-255)
    return raw * 4            # scale 0–1020

# -----------------------------
# GPIO setup
# -----------------------------
GPIO.setmode(GPIO.BCM)#BCM pin numbering

GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)#seting up button 1 as input with pull up resistor
GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)#seting up button 2 as input with pull up resistor
GPIO.setup(BUTTON_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)#seting up button 3 as input with pull up resistor
GPIO.setup(BUTTON_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)#seting up button 4 as input with pull up resistor

# -----------------------------
# Shift Register
# -----------------------------
class ShiftRegister:
# class for controlling the 74HC595 shift register
    def __init__(self, data_pin=22, clock_pin=17, latch_pin=27):#initalize shift register with data, clock, and latch pins

        self.data_pin = data_pin#serial data input
        self.clock_pin = clock_pin#shift clock
        self.latch_pin = latch_pin#storage/latch clock

        GPIO.setup(self.data_pin, GPIO.OUT)#seting up data pin as output
        GPIO.setup(self.clock_pin, GPIO.OUT)#seting up clock pin as output
        GPIO.setup(self.latch_pin, GPIO.OUT)#seting up latch pin as output

    def write_one_bit(self, bit):#write one bit to the shift register

        GPIO.output(self.data_pin, bit)#send bit to data pin

        GPIO.output(self.clock_pin, GPIO.HIGH)#pulse the clock pin
        GPIO.output(self.clock_pin, GPIO.LOW)#pulse the clock pin

    def copy_to_storage_register(self):#copy data from shift register to storage register

        GPIO.output(self.latch_pin, GPIO.HIGH)#pulse the latch pin
        GPIO.output(self.latch_pin, GPIO.LOW)#pulse the latch pin

    def write_byte(self, data):#write one byte to the shift register

        mask = 0b10000000#mask to get the most significant bit

        for _ in range(8):

            bit = (data & mask) != 0#check if the most significant bit is 1
            self.write_one_bit(bit)#write the bit to the shift register

            mask >>= 1#shift the mask to the right

    def shift_out_16bit(self, value):#write 16 bits to the shift register

        high_byte = (value >> 8) & 0xFF#get the most significant byte
        low_byte = value & 0xFF#get the least significant byte

        self.write_byte(high_byte)#write the most significant byte to the shift register
        self.write_byte(low_byte)#write the least significant byte to the shift register

        self.copy_to_storage_register()#copy data from shift register to storage register

    def clear(self):#clears the shift register by sending out 16 bits that are all 0
        self.shift_out_16bit(0)#shift out 0 to clear the shift register

# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":#main function

    shift_reg = ShiftRegister()#create shift register

    fill_mode = True#fill mode
    inverted = False#inverted mode

    try:

        while True:#loop forever

            # -----------------------------
            # BUTTONS
            # -----------------------------

            if GPIO.input(BUTTON_1) == 0:#button 1 is pressed
                fill_mode = False#set fill mode to false
                print("Single LED mode")#print single LED mode
                time.sleep(0.2)#wait for 0.2 seconds

            if GPIO.input(BUTTON_2) == 0:#button 2 is pressed
                fill_mode = True#set fill mode to true
                print("Fill mode")#print fill mode
                time.sleep(0.2)#wait for 0.2 seconds

            if GPIO.input(BUTTON_3) == 0:#button 3 is pressed
                shift_reg.clear()#clear the shift register
                print("Cleared LEDs")#print cleared LEDs
                time.sleep(0.2)#wait for 0.2 seconds

            if GPIO.input(BUTTON_4) == 0:#button 4 is pressed
                inverted = not inverted#invert the mode
                print("Invert toggled")#print invert toggled
                time.sleep(0.2)#wait for 0.2 seconds

            # -----------------------------
            # JOYSTICK
            # -----------------------------

            value = read_channel(X_JOYSTICK)#read ADC value

            # map joystick to LED position
            led_pos = int(value / 102)#map joystick value to LED position

            if led_pos > 9:#if LED position is greater than 9
                led_pos = 0#set LED position to 9
            elif led_pos < 0:#if LED position is less than 0
                led_pos = 9#set LED position to 9

            # invert direction
            if inverted:#invert the mode
                led_pos = 9 - led_pos#invert the LED position

            # -----------------------------
            # CREATE PATTERN
            # -----------------------------

            if fill_mode:#fill mode
                pattern = (1 << (led_pos + 1)) - 1#create pattern
            else:#single LED mode
                pattern = (1 << led_pos)#create pattern

            shift_reg.shift_out_16bit(pattern)#send pattern to shift register

            print(f"X={value} LED={led_pos} Pattern={pattern:010b}")#print pattern

            time.sleep(0.05)#wait for 0.05 seconds

    except KeyboardInterrupt:
        pass#exit the loop

    finally:
        shift_reg.clear()#clear the shift register
        GPIO.cleanup()#cleanup GPIO