from time import sleep
import smbus2

bus = smbus2.SMBus(1)
ADC_ADDRESS = 0x48

def read_adc(channel):
    bus.write_byte(ADC_ADDRESS, 0x40 + channel)
    bus.read_byte(ADC_ADDRESS)         # dummy read
    value = bus.read_byte(ADC_ADDRESS) # real read
    return value

try:
    while True:
        pot0 = read_adc(0)
        joy_x = read_adc(6)
        print(f"ADC0={pot0}   ADC6={joy_x}")
        sleep(0.2)

except KeyboardInterrupt:
    print("Stopped")