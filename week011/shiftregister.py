import time
from gpiozero import OutputDevice

DS   = 22
STCP = 27
SHCP = 17

class ShiftRegister:
    MSB_TO_LSB = "MSB TO LSB"
    LSB_TO_MSB = "LSB TO MSB"

    def __init__(self):
        self._ds   = OutputDevice(DS,   active_high=True, initial_value=False)
        self._stcp = OutputDevice(STCP, active_high=True, initial_value=False)
        self._shcp = OutputDevice(SHCP, active_high=True, initial_value=False)

    def pulse(self, pin):
        pin.on()
        time.sleep(0.000001)
        pin.off()
        time.sleep(0.000001)

    def shift_byte_out(self, byte, direction=MSB_TO_LSB):
        byte &= 0xFF
        bit_range = range(7, -1, -1) if direction == self.MSB_TO_LSB else range(8)
        for i in bit_range:
            if (byte >> i) & 1:
                self._ds.on()
            else:
                self._ds.off()
            self.pulse(self._shcp)

    def shift_out_16bit(self, value, direction=MSB_TO_LSB):
        value &= 0xFFFF
        self.shift_byte_out((value >> 8) & 0xFF, direction)
        self.shift_byte_out(value & 0xFF, direction)
        self.pulse(self._stcp)

    def clear(self):
        self.shift_out_16bit(0x0000)

    def close(self):
        self._ds.close()
        self._stcp.close()
        self._shcp.close()
