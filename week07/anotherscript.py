from time import sleep
import smbus2

bus = smbus2.SMBus(1)
ADC_ADDRESS = 0x48

def read_adc(channel):
    # select channel
    bus.write_byte(ADC_ADDRESS, 0x40 + channel)

    # throw away first read after switching channel
    bus.read_byte(ADC_ADDRESS)
    bus.read_byte(ADC_ADDRESS)

    # use third read as the stable value
    return bus.read_byte(ADC_ADDRESS)

try:
    while True:
        ch0 = read_adc(0)
        ch1 = read_adc(1)
        ch2 = read_adc(2)
        ch3 = read_adc(3)

        print(f"CH0={ch0:3}  CH1={ch1:3}  CH2={ch2:3}  CH3={ch3:3}")
        sleep(0.3)

except KeyboardInterrupt:
    print("Stopped")