import os
import time

os.environ.setdefault("RPI_LGPIO_CHIP", "0")

import smbus


class ADCReader:
    """ADS7830 ADC helper used on the Freenove Projects Board."""

    ADC_COMMANDS = {
        0: 0x84,
        1: 0xC4,
        2: 0x94,
        3: 0xD4,
        4: 0xA4,
        5: 0xE4,
        6: 0xB4,
        7: 0xF4,
    }

    def __init__(self, address=0x48, bus_number=1):
        self.address = address
        self.bus = smbus.SMBus(bus_number)

    def read(self, channel):
        self.bus.write_byte(self.address, self.ADC_COMMANDS[channel])
        time.sleep(0.002)
        return self.bus.read_byte(self.address)

    def close(self):
        try:
            self.bus.close()
        except AttributeError:
            pass


class Potentiometer:
    def __init__(self, adc, channel=2):
        self.adc = adc
        self.channel = channel

    def read(self):
        return self.adc.read(self.channel)

    def percent(self):
        return round((self.read() / 255) * 100)
