import time
from shift_register import ShiftRegister


class LedMatrix8x8:
    def __init__(self, shift_register):
        self.shift_register = shift_register
        self.row_data = [0x00] * 8

    def toggle_pixel(self, x, y):
        self.row_data[y] ^= (1 << x)

    def set_pixel(self, x, y):
        self.row_data[y] |= (1 << x)

    def clear_pixel(self, x, y):
        self.row_data[y] &= ~(1 << x)

    def clear(self):
        self.row_data = [0x00] * 8

    def refresh_once(self, cursor_x=None, cursor_y=None, cursor_visible=False):
        for row in range(8):
            row_byte = 1 << row
            col_byte = self.row_data[row]

            if cursor_visible and row == cursor_y:
                col_byte |= (1 << cursor_x)

            # common anode: invert columns
            col_byte = ~col_byte & 0xFF

            value = (row_byte << 8) | col_byte

            self.shift_register.shift_out_16bit(
                value,
                direction=ShiftRegister.LSB_TO_MSB
            )

            time.sleep(0.001)