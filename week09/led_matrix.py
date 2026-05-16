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
        for row in range(8):#loops through each row
            row_byte = 1 << row#selects the row to be displayed
            col_byte = self.row_data[row]#column data for the selected row

            if cursor_visible and cursor_y == row:#cursor overlay
                col_byte ^= (1 << cursor_x)#cursor overlay

            col_byte = ~col_byte & 0xFF#inverts the column data

            value = (col_byte << 8) | row_byte#packs the column and row data together

            self.shift_register.shift_out_16bit(#shifts the data out to the shift register
                value,#the value to be shifted out
                direction=ShiftRegister.LSB_TO_MSB#sets the direction to LSB to MSB
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