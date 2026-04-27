import time
from shift_register import ShiftRegister# we import shift_register.py so we can use its functions

class LedMatrix8x8:# led matrix class
    ROW_DELAY = 0.0005# this is the delay between rows in ms

    def __init__(self, shift_register):# constructor
        self.shift_register = shift_register# we pass the shift register object to the matrix
        self.row_data = [0x00] * 8# this is the data for the rows

    def toggle_pixel(self, x, y):# this function toggles a pixel
        self.row_data[y] ^= (1 << x)# we toggle the pixel at (x, y)

    def get_pixel(self, x, y):# this function gets the pixel at (x, y)
        return (self.row_data[y] >> x) & 1# we get the pixel at (x, y)

    def clear(self):# this function clears the matrix
        self.row_data = [0x00] * 8# we set all the pixels to off

    def refresh_once(self, cursor_x=None, cursor_y=None, cursor_visible=False):# this function refreshes the matrix once
        for row in range(8):# we loop through each row
            row_byte = 1 << row# we set the row byte
            col_byte = self.row_data[row]# we get the column byte

            if cursor_visible and cursor_y == row:# if the cursor is visible and the cursor y is equal to the row
                col_byte ^= (1 << cursor_x)# we toggle the pixel at (x, y)

            col_byte = ~col_byte & 0xFF# we invert the column byte

            # If your matrix is wrong, swap this line with the alternative below
            value = (col_byte << 8) | row_byte# we combine the column byte and the row byte

            # Alternative:
            # value = (row_byte << 8) | col_byte# this is the alternative way to combine the column byte and the row byte

            self.shift_register.shift_out_16bit(
                value,#
                direction=ShiftRegister.LSB_TO_MSB# this is the direction of the shift register
            )

            time.sleep(self.ROW_DELAY)#

    def blank(self):# this function blanks the matrix
        self.shift_register.shift_out_16bit(
            0x00FF,# this is the value to be shifted out
            direction=ShiftRegister.LSB_TO_MSB# this is the direction of the shift register
        )