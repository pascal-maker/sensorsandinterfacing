import RPi.GPIO as GPIO
import smbus
import time

fill_mode = False   # global variable: False = single LED, True = fill mode

# ADC setup Read potentiometer (A2)
ADC_ADDRESS = 0x48   # I2C address of the ADC #address of ADC chip
#not something you invent → hardware defined
A2 = 2               # potentiometer is connected to channel A2
bus = smbus.SMBus(1) # use I2C bus 1

def read_adc(channel):
    bus.write_byte(ADC_ADDRESS, 0x40 | channel)  # select ADC channel
    return bus.read_byte(ADC_ADDRESS)            # read value from ADC

def scale_to_1_10(value):#Scale this value into 1-10 range, show on LED Bar Graph
    scaled = int((value / 255) * 10)  # convert ADC value to 0-10 range
    if scaled < 1:
        scaled = 1                    # keep minimum at 1
    if scaled > 10:
        scaled = 10                   # keep maximum at 10
    return scaled

def toggle_fill(channel):
    global fill_mode
    fill_mode = not fill_mode         # toggle fill mode when button is pressed


# Shift register class
class ShiftRegister:
    def __init__(self, data_pin=22, clock_pin=17, latch_pin=27):
        self.data_pin = data_pin      # DS pin
        self.clock_pin = clock_pin    # SHCP pin
        self.latch_pin = latch_pin    # STCP pin
        self._setup()                 # run setup immediately

    def _setup(self):
        GPIO.setmode(GPIO.BCM)                    # use BCM numbering
        GPIO.setup(self.data_pin, GPIO.OUT)       # data pin is output
        GPIO.setup(self.clock_pin, GPIO.OUT)      # shift clock pin is output
        GPIO.setup(self.latch_pin, GPIO.OUT)      # latch clock pin is output

        GPIO.output(self.data_pin, GPIO.LOW)      # start data pin LOW
        GPIO.output(self.clock_pin, GPIO.LOW)     # start shift clock LOW
        GPIO.output(self.latch_pin, GPIO.LOW)     # start latch clock LOW

    def write_one_bit(self, bit):
        GPIO.output(self.data_pin, GPIO.HIGH if bit else GPIO.LOW)  # put bit on DS
        GPIO.output(self.clock_pin, GPIO.HIGH)                      # pulse shift clock HIGH
        GPIO.output(self.clock_pin, GPIO.LOW)                       # back LOW

    def copy_to_storage_register(self):
        GPIO.output(self.latch_pin, GPIO.HIGH)  # pulse latch HIGH
        GPIO.output(self.latch_pin, GPIO.LOW)   # back LOW

    def reset_storage_register(self):
        self.shift_out_16bit(0)  # send 16 zeros to turn all LEDs off

    def write_byte(self, data_byte):
        mask = 0b10000000                 # start with the leftmost bit
        for _ in range(8):                # repeat for 8 bits
            bit = (data_byte & mask) != 0 # get current bit
            self.write_one_bit(bit)       # send current bit
            mask >>= 1                    # shift mask right

    def shift_out_16bit(self, value):
        high_byte = (value >> 8) & 0xFF   # upper 8 bits
        low_byte = value & 0xFF           # lower 8 bits

        self.write_byte(high_byte)        # send high byte
        self.write_byte(low_byte)         # send low byte
        self.copy_to_storage_register()   # latch result to outputs

    def clear(self):
        self.reset_storage_register()     # clear LEDs


# LED bar graph class
class LedBarGraph:
    def __init__(self, shift_register):
        self.shift_register = shift_register   # store shift register object

    def set_pattern(self, value, fill=False):
        if value < 0:
            value = 0
        if value > 10:
            value = 10

        if value == 0:
            pattern = 0                    # all LEDs off
        elif fill:
            pattern = (1 << value) - 1     # fill LEDs up to value
        else:
            pattern = 1 << (value - 1)     # turn on only one LED

        self.shift_register.shift_out_16bit(pattern)  # send pattern to LED bar

    def clear(self):
        self.shift_register.clear()        # clear all LEDs


# Buzzer setupCreate a low pitch tone for lower values, and increase the pitch of the sound while the analog value increases
GPIO.setmode(GPIO.BCM)       # use BCM numbering
buzzer_pin = 12              # buzzer connected to GPIO 12
GPIO.setup(buzzer_pin, GPIO.OUT)
buzzer_pwm = GPIO.PWM(buzzer_pin, 200)  # create PWM on buzzer pin with start frequency 200 Hz
buzzer_pwm.start(0)                     # start PWM with duty cycle 0 (silent)

# Button setup
BUTTON_PIN = 20#Use button GPIO 20 to toggle between “filling” the LED Bar graph, or just showing a single LED (event/interrupt)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # button as input with pull-up
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=toggle_fill, bouncetime=200)

# Create objects
shift_reg = ShiftRegister()
led_bar = LedBarGraph(shift_reg)

try:
    while True:
        adc_value = read_adc(A2)                     # read potentiometer from channel A2
        scaled_value = scale_to_1_10(adc_value)      # convert to 1-10

        led_bar.set_pattern(scaled_value, fill_mode) # show value on LED bar

        frequency = 200 + (scaled_value - 1) * 80    # map value to buzzer pitch
        buzzer_pwm.ChangeFrequency(frequency)        # change sound frequency
        buzzer_pwm.ChangeDutyCycle(50)               # turn buzzer on with 50% duty cycle

        time.sleep(0.1)                              # small delay

except KeyboardInterrupt:
    pass

finally:
    buzzer_pwm.ChangeDutyCycle(0)  # turn buzzer silentMake sure the buzzer stops outputting sound when the program ends.
    buzzer_pwm.stop()              # stop PWM
    led_bar.clear()                # turn LEDs off
    GPIO.cleanup()                 # reset GPIO pins