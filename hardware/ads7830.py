"""ADS7830 8-channel, 8-bit I2C analog-to-digital converter."""

try:
    from smbus2 import SMBus
except ImportError:
    from smbus import SMBus


class ADS7830:
    CHANNEL_COMMANDS = (0x84, 0xC4, 0x94, 0xD4, 0xA4, 0xE4, 0xB4, 0xF4)

    def __init__(self, address=0x48, bus_id=1, vref=3.3):
        self.address = address
        self.vref = vref
        self.bus = SMBus(bus_id)

    def read_raw(self, channel):
        """Return the selected channel as an integer from 0 through 255."""
        if not 0 <= channel <= 7:
            raise ValueError("ADS7830 channel must be between 0 and 7")
        self.bus.write_byte(self.address, self.CHANNEL_COMMANDS[channel])
        return self.bus.read_byte(self.address)

    def read_voltage(self, channel):
        return self.read_raw(channel) * self.vref / 255.0

    def close(self):
        self.bus.close()

    cleanup = close
