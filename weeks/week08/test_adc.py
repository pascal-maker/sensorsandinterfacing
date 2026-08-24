import smbus2
import time

# ADS7830 I2C address
ADDRESS = 0x48

# Open I2C bus
bus = smbus2.SMBus(1)

# Correct ADS7830 channel command mapping
COMMANDS = [
    0x84,  # CH0
    0xC4,  # CH1
    0x94,  # CH2
    0xD4,  # CH3
    0xA4,  # CH4
    0xE4,  # CH5
    0xB4,  # CH6
    0xF4   # CH7
]

def read_channel(channel):

    command = COMMANDS[channel]

    bus.write_byte(ADDRESS, command)

    return bus.read_byte(ADDRESS)

try:

    while True:

        values = []

        for ch in range(8):

            value = read_channel(ch)

            values.append(f"CH{ch}: {value:3}")

        print(" | ".join(values))

        time.sleep(0.2)

except KeyboardInterrupt:

    print("Stopped")