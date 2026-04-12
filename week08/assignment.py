

class ShiftRegister:import RPi.GPIO as GPIO
import smbus
import time


fill_mode = False

#ADC setup
ADC_ADDRESS = 0x48
A2 = 2
bus = smbus.SMBus(1)

def read_adc(channel):
    bus.write_byte(ADC_ADDRESS,0x40| channel)
    return bus.read_byte(ADC_ADDRESS)

def scale_to_1_10(value):
    scaled = int((value/255 *10))
    if scaled < 1:
        scaled =1
    if scaled  > 10:
        scaled = 10
    return scaled    
        

def toggle_fill(channel):
    global fill_mode
    fill_mode = not fill_mode



# setup shift register

class ShiftRegister:
    def __init__(self, data_pin=22, clock_pin=17, latch_pin=27):#
        self.data_pin = data_pin
        self.clock_pin = clock_pin
        self.latch_pin = latch_pin
        self._setup()

    
    def _setup(self):
        GPIO.setmode(GPIO.BCM)                    # use BCM pin numbering
        GPIO.setup(self.data_pin, GPIO.OUT)       # data pin is output
        GPIO.setup(self.clock_pin, GPIO.OUT)      # shift clock pin is output
        GPIO.setup(self.latch_pin, GPIO.OUT)      # latch clock pin is output

        GPIO.output(self.data_pin, GPIO.LOW)      # start data pin LOW
        GPIO.output(self.clock_pin, GPIO.LOW)     # start shift clock LOW
        GPIO.output(self.latch_pin, GPIO.LOW)     # start latch clock LOW
    
    
    def write_one_bit(self, bit):
        GPIO.output(self.data_pin, GPIO.HIGH if bit else GPIO.LOW)  # put bit on DS
        GPIO.output(self.clock_pin, GPIO.HIGH)                      # rising edge → shift
        GPIO.output(self.clock_pin, GPIO.LOW)                       # back to LOW

    def copy_to_storage_register(self):
        GPIO.output(self.latch_pin, GPIO.HIGH)  # rising edge → update outputs
        GPIO.output(self.latch_pin, GPIO.LOW)

    def reset_storage_register(self):
        self.shift_out_16bit(0)  # send all 0 → all LEDs off

    def write_byte(self, data_byte):
        mask = 0b10000000                 # start from MSB (leftmost bit)
        for _ in range(8):                # 8 bits
            bit = (data_byte & mask) != 0 # extract current bit
            self.write_one_bit(bit)       # send bit
            mask >>= 1                   # move mask right

    def shift_out_16bit(self, value):
        high_byte = (value >> 8) & 0xFF   # upper 8 bits
        low_byte = value & 0xFF           # lower 8 bits

        self.write_byte(high_byte)        # send first byte
        self.write_byte(low_byte)         # send second byte
        self.copy_to_storage_register()   # latch → show on LEDs

    def clear(self):
        self.reset_storage_register()    


class LedBarGraph:
    # class for controlling the 10-LED bar graph
    def __init__(self, shift_register):
        self.shift_register = shift_register   # store the shift register object

    def set_pattern(self, value, fill=False):
        # keep value between 0 and 10
        if value < 0:
            value = 0
        if value > 10:
            value = 10

        # if value is 0, no LEDs must be on
        if value == 0:
            pattern = 0

        # if fill is True, turn on all LEDs from 1 up to value
        elif fill:
            pattern = (1 << value) - 1

        # if fill is False, turn on only one LED
        else:
            pattern = 1 << (value - 1)

        # send the pattern to the 2 shift registers
        self.shift_register.shift_out_16bit(pattern)

    def clear(self):
        # turn all LEDs off
        self.shift_register.clear()
         # clear all LEDs

# setup buzzer
GPIO.setmode(GPIO.BCM)       # use BCM numbering for the GPIO pins

buzzer_pin = 12              # the buzzer is connected to GPIO 12

GPIO.setup(buzzer_pin, GPIO.OUT) 
buzzer_pwm = GPIO.PWM(buzzer_pin, 200)
buzzer_pwm.start(0)

#button
BUTTON_PIN = 20
GPIO.setup(BUTTON_PIN,GPIO.IN,pull_up_down=GPIO.PUD_UP) 
GPIO.add_event_detect(BUTTON_PIN,GPIO.FALLING,callback=toggle_fill,bouncetime=200)
shift_reg = ShiftRegister()
led_bar = LedBarGraph(shift_reg)


try:
    while True:
        adc_value = read_adc(A2)
        scaled_value = scale_to_1_10(adc_value)
        led_bar.set_pattern(scaled_value, fill_mode)


        frequency = 200 + (scaled_value - 1) * 80

        buzzer_pwm.ChangeFrequency(frequency)
        buzzer_pwm.ChangeDutyCycle(50)

        time.sleep(0.1)

except KeyboardInterrupt:
    pass
finally:
    buzzer_pwm.ChangeDutyCycle(0)
    buzzer_pwm.stop()
    led_bar.clear()
    # stop buzzer
    GPIO.cleanup()