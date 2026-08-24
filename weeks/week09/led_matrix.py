import time
from shift_register import ShiftRegister#imports the shift register

class LedMatrix8x8:#creates the led matrix class
    ROW_DELAY = 0.0005  #sets the delay between rows

    def __init__(self, shift_register):#initialize the led matrix
        self.shift_register = shift_register#stores the shift register
        self.row_data = [0x00] * 8#row data for each pixel

    def toggle_pixel(self, x, y):#toggles the pixel at the given x and y coordinates
        self.row_data[y] ^= (1 << x)#toggles the pixel at the given x and y coordinates

    def get_pixel(self, x, y):#gets the pixel at the given x and y coordinates
        return (self.row_data[y] >> x) & 1#gets the pixel at the given x and y coordinates

    def clear(self):#clears the led matrix
        self.row_data = [0x00] * 8#clears the led matrix

    def refresh_once(self, cursor_x=None, cursor_y=None, cursor_visible=False):# refreshes the led matrix once
        # The physical matrix is multiplexed one column at a time. row_data is
        # stored in the convenient drawing format row_data[y], so each scan
        # transposes one vertical column into an 8-bit row pattern.
        for column in range(8):
            row_byte = 0

            for row in range(8):
                pixel_on = (self.row_data[row] >> column) & 1

                # XOR overlays the blinking cursor without permanently adding
                # it to row_data. On a saved dot, the cursor visibly blinks it.
                if cursor_visible and cursor_x == column and cursor_y == row:
                    pixel_on ^= 1

                if pixel_on:
                    row_byte |= 1 << row

            # Matrix column selection is active-low. Begin at the leftmost
            # selector (0x80), move right, and invert so only that column is LOW.
            column_byte = ~(0x80 >> column) & 0xFF
            value = (row_byte << 8) | column_byte

            # The Freenove two-register cascade transmits both bytes MSB-first.
            self.shift_register.shift_out_16bit(
                value,
                direction=ShiftRegister.MSB_TO_LSB,
            )

            time.sleep(self.ROW_DELAY)#pauses for the row delay

    def blank(self):#clears the led matrix
        self.shift_register.shift_out_16bit(#shifts the data out to the shift register
            0x00FF,#clears the led matrix
            direction=ShiftRegister.LSB_TO_MSB#sets the direction to LSB to MSB
        )#turns the whole display dark

#This class:

#stores LED states
#converts rows into bytes
#multiplexes rows rapidly
#uses bit operations for pixels
#sends serial data through shift registers
