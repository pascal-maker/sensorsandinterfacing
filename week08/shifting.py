import RPi.GPIO as GPIO   # library to control Raspberry Pi GPIO pins
import smbus2
import time

BUTTON_1 = 20#Button GPIO 20
BUTTON_2 = 16#Button GPIO 16
BUTTON_3 = 21#Button GPIO 21
BUTTON_4 = 26#Button GPIO 26

X_JOYSTICK = 0  # PCF8591 channel 0 (joystick X-axis)
Y_JOYSTICK = 1  # PCF8591 channel 1 (joystick Y-axis)

chip = 0x48          # PCF8591 default I2C address
bus = smbus2.SMBus(1)  # I2C bus 1 on Raspberry Pi


def read_channel(channel):
    # PCF8591: send control byte (0x40 | channel) then read one byte (0-255)
    bus.write_byte(chip, 0x40 | (channel & 0x03))
    bus.read_byte(chip)          # dummy read — returns previous conversion
    raw = bus.read_byte(chip)    # actual 8-bit ADC value (0-255)
    return raw * 4               # scale to 0-1020 to match 10-bit thresholds

# setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)#seting up button 1 as input with pull up resistor
GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)#seting up button 2 as input with pull up resistor
GPIO.setup(BUTTON_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)#seting up button 3 as input with pull up resistor
GPIO.setup(BUTTON_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)#seting up button 4 as input with pull up resistor



class ShiftRegister:
    # class for controlling the 74HC595 shift register
    def __init__(self, data_pin=22, clock_pin=17, latch_pin=27):
        self.data_pin = data_pin      # DS = Serial Data pin means send data from pi to the shift register
        self.clock_pin = clock_pin    # SHCP = Shift Clock pin means pulse this pin to send the data 
        self.latch_pin = latch_pin    # STCP = Latch / Storage Clock pin means pulse this pin to copy the data from shift register to output pins
        self._setup()                 # run GPIO setup immediately 

    def _setup(self):
        GPIO.setmode(GPIO.BCM)                    # use BCM pin numbering
        GPIO.setup(self.data_pin, GPIO.OUT)       # data pin is output
        GPIO.setup(self.clock_pin, GPIO.OUT)      # shift clock pin is output
        GPIO.setup(self.latch_pin, GPIO.OUT)      # latch clock pin is output

        GPIO.output(self.data_pin, GPIO.LOW)      # start data pin LOW
        GPIO.output(self.clock_pin, GPIO.LOW)     # start shift clock LOW
        GPIO.output(self.latch_pin, GPIO.LOW)     # start latch clock LOW

    def write_one_bit(self, bit):#write one bit to the shift register
        # put the bit on the data pin
        GPIO.output(self.data_pin, GPIO.HIGH if bit else GPIO.LOW)#if bit is HIGH, set the data pin to HIGH, else set the data pin to LOW

        # create a pulse on the shift clock
        # LOW -> HIGH is the rising edge
        # at that moment the shift register reads DS
        GPIO.output(self.clock_pin, GPIO.HIGH)#set shift clock to HIGH, this will cause the shift register to read the data pin
        GPIO.output(self.clock_pin, GPIO.LOW)#set shift clock to LOW, this will cause the shift register to shift the data to the next position

    def copy_to_storage_register(self):#copy the data from the shift register to the output pins
        # create a pulse on the latch pin
        # this copies the internal shift register data to the outputs
        GPIO.output(self.latch_pin, GPIO.HIGH)#set latch pin to HIGH, this will cause the shift register to copy the data to the output pins
        GPIO.output(self.latch_pin, GPIO.LOW)#set latch pin to LOW, this will cause the shift register to copy the data to the output pins

    def reset_storage_register(self):#reset the storage register
        # clear both cascaded shift registers by sending 16 zeros
        self.shift_out_16bit(0)

    def write_byte(self, data_byte):#write a byte to the shift register
        # start with mask 10000000 so we check the leftmost bit first
        mask = 0b10000000#mask to check the leftmost bit first

        # loop 8 times because 1 byte = 8 bits
        for _ in range(8):#loop 8 times because 1 byte = 8 bits
            # check if the current masked bit is 1 or 0
            bit = (data_byte & mask) != 0#if the current masked bit is 1 or 0, then 

            # send that bit to the shift register
            self.write_one_bit(bit)#write one bit to the shift register

            # move mask one place to the right
            mask >>= 1#shift mask one place to the right

    def shift_out_16bit(self, value):#take the upper 8 bits and the lower 8 bits
        # take the upper 8 bits
        high_byte = (value >> 8) & 0xFF#take the upper 8 bits

        # take the lower 8 bits
        low_byte = value & 0xFF#take the lower 8 bits

        # send both bytes one after another
        self.write_byte(high_byte)#send the upper 8 bits to the shift register
        self.write_byte(low_byte)#send the lower 8 bits to the shift register

        # latch the result so the LEDs update
        self.copy_to_storage_register()#copy the data from the shift register to the output pins

    def clear(self):#clear the LEDs
        # easier name for clearing everything
        self.reset_storage_register()#reset the storage register


class LedBarGraph:#class for controlling the 10-LED bar graph
    def __init__(self, shift_register):#store the shift register object
        self.shift_register = shift_register   # store the shift register object

    def set_pattern(self, value, fill=False):#set the pattern of the LEDs
        # keep value between 0 and 10
        if value < 0:#if value is less than 0
            value = 0
        if value > 10:#if value is greater than 10
            value = 10

        # if value is 0, no LEDs must be on
        if value == 0:#if value is 0, then turn off all the LEDs
            pattern = 0 #turn off all the LEDs

        # if fill is True, turn on all LEDs from 1 up to value
        elif fill:#if fill is True, turn on all LEDs from 1 up to value
            pattern = (1 << value) - 1#turn on all LEDs from 1 up to value

        # if fill is False, turn on only one LED
        else:#if fill is False, turn on only one LED
            pattern = 1 << (value - 1)#turn on only one LED

        # send the pattern to the 2 shift registers
        self.shift_register.shift_out_16bit(pattern)#send the pattern to the 2 shift registers

    def clear(self):#clear the LEDs
        # turn all LEDs off
        self.shift_register.clear()#clear the LEDs


if __name__ == "__main__":
    try:
        # create the shift register object
        shift_reg = ShiftRegister()#create the shift register object

        # create the LED bar object and give it the shift register
        led_bar = LedBarGraph(shift_reg)#create the LED bar object and give it the shift register

        # keep asking the user for input
        while True:#keep asking the user for input

            value = read_channel(X_JOYSTICK)#read the value from the joystick

            # center zone
            if 450 <= value <= 550:#if the value is between 450 and 550
                pattern = 0b0001100000

            # left side
            elif value < 450:#if the value is less than 450
                leds = int((450 - value) / 90)#calculate the number of LEDs to turn on
                pattern = 0#initialize the pattern to 0
                for i in range(leds + 2):#loop through the LEDs
                    pos = 4 - i  # start at bit 4 (adjacent to center), go left
                    if pos >= 0:#if the position is greater than or equal to 0
                        pattern |= (1 << pos)#turn on the LED at the current position

            # right side
            else:#if the value is greater than 450
                leds = int((value - 550) / 90)#calculate the number of LEDs to turn on
                pattern = 0#initialize the pattern to 0
                for i in range(leds + 2):#loop through the LEDs
                    pos = 5 + i  # start at bit 5 (adjacent to center), go right
                    if pos <= 9:#if the position is less than or equal to 9
                        pattern |= (1 << pos)#turn on the LED at the current position

            shift_reg.shift_out_16bit(pattern)#send the pattern to the 2 shift registers
            print(f"X: {value}  pattern: {pattern:010b}")#print the pattern to the console
            
            

    except KeyboardInterrupt:#stop safely with Ctrl + C
        pass

    finally:
        # reset GPIO pins when the program ends
        GPIO.cleanup()