import smbus
import time

bus = smbus.SMBus(1)
ADC_ADDRESS = 0x48

def read_adc(channel):
    bus.write_byte(ADC_ADDRESS, 0x40 | channel)
    bus.read_byte(ADC_ADDRESS)        # discard stale result
    return bus.read_byte(ADC_ADDRESS) # actual value

try:
    while True:
        x = read_adc(0)  # VRX on AIN0
        y = read_adc(1)  # VRY on AIN1

        print(f"X: {x:3}  Y: {y:3}")
        time.sleep(0.1)

except KeyboardInterrupt:
    pass