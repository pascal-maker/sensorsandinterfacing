import time
from shift_register import ShiftRegister#imports the shift register

class LedMatrix8x8:#creates the led matrix class
    ROW_DELAY = 0.001  #sets the delay between columns

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
        # Freenove's common-anode circuit scans one active-low column at a
        # time. Build the eight active-high row bits for that column.
        for column in range(8):
            row_byte = 0
            for row in range(8):
                pixel_on = (self.row_data[row] >> column) & 1
                if cursor_visible and cursor_x == column and cursor_y == row:
                    pixel_on ^= 1
                if pixel_on:
                    row_byte |= 1 << row

            column_byte = ~(0x80 >> column) & 0xFF
            value = (row_byte << 8) | column_byte

            self.shift_register.shift_out_16bit(
                value,
                direction=ShiftRegister.MSB_TO_LSB,
            )

            time.sleep(self.ROW_DELAY)#pauses for the row delay

    def blank(self):#clears the led matrix
        self.shift_register.shift_out_16bit(#shifts the data out to the shift register
            0x00FF,#clears the led matrix
            direction=ShiftRegister.MSB_TO_LSB#sets the direction to MSB to LSB
        )#turns the whole display dark

#This class:

#stores LED states
#converts rows into bytes
#multiplexes rows rapidly
#uses bit operations for pixels
#sends serial data through shift registers
