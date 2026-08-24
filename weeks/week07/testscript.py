import smbus, time
bus = smbus.SMBus(1)
ADC_ADDRESS = 0x48
def read_adc(channel):
    cmd = 0x84 | ((channel & 0x03) << 4) | ((channel & 0x04) << 1)
    bus.write_byte(ADC_ADDRESS, cmd)
    bus.read_byte(ADC_ADDRESS)
    return bus.read_byte(ADC_ADDRESS)

while True:
    for ch in range(8):
        print(f"CH{ch}: {read_adc(ch):3}", end="  ")
    print()
    time.sleep(0.5)
  #A4 for channel 6 & channel 2 A a2 is for channel 1 and channel 5 channel 0 and 3 with joystick on gpio button 7    