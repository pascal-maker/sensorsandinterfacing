import time
from shiftregister import ShiftRegister

class LEDMatrix8x8:#class for the 8x8 led matrix
    ROWS = {#the rows dictionary this tells us the bit position for each row 
        0: 1 << 0,#row 0 with bit position 0
        1: 1 << 1,#row 1 with bit position 1
        2: 1 << 2,#row 2 with bit position 2
        3: 1 << 3,#row 3 with bit position 3
        4: 1 << 4,#row 4 with bit position 4
        5: 1 << 5,#row 5 with bit position 5
        6: 1 << 6,#row 6 with bit position 6
        7: 1 << 7,#row 7 with bit position 7
    }
    def __init__(self,shift_register,common_anode=True):#initializes the 8x8 led matrix
        self._sr = shift_register#the shift register to control the display
        self._common_anode = common_anode#the type of display
        self.pattern = [0x00]*8#the pattern of the 8x8 led matrix

    def setPattern(self,pattern):#sets the pattern of the 8x8 led matrix
        if len(pattern) != 8:#checks if the pattern is 8 bytes long
            raise ValueError("Pattern must be 8 bytes long")#raises an error if the pattern is not 8 bytes long
        self.pattern = [byte & 0xFF for byte in pattern]#sets the pattern of the 8x8 led matrix
        
    
    def refresh_once(self):#refreshes the 8x8 led matrix once
        for row_index,col_byte in enumerate(self.pattern):#iterates through the pattern
            row_byte = self.ROWS[row_index]#gets the row byte for each row
            if self._common_anode:#checks if the display is common anode
                col_byte = ~col_byte & 0xFF#inverts the column byte

            value = (row_byte << 8 )| col_byte#combines the row and column bytes

            self._sr.shift_out_16bit(value,direction=ShiftRegister.LSB_TO_MSB)    #shifts the value to the shift register
            time.sleep(0.001)#waits for 0.001 seconds
    