import time

class FourDigit7Segment:
    # --- Segment constants ---
    # Each letter maps to one bit in a byte.
    # That byte is sent to the shift register to control which segments light up on one digit.
    A  = 1<<0   # bit 0 = 0b00000001
    B  = 1<<1
    C  = 1<<2
    D  = 1<<3
    E  = 1<<4
    F  = 1<<5
    G  = 1<<6
    DP = 1<<7   # decimal point

    # --- Font table (common-cathode) ---
    # Maps each character to the set of segments that must be ON to draw it.
    # Written for common-cathode where 1 = segment on.
    CATHODE_SEGMENTS = {
        0: A|B|C|D|E|F,
        1: B|C,
        2: A|B|D|E|G,
        3: A|B|C|D|G,
        4: B|C|F|G,
        5: A|C|D|F|G,
        6: A|C|D|E|F|G,
        7: A|B|C,
        8: A|B|C|D|E|F|G,
        9: A|B|C|D|F|G,
        "A": A|B|C|E|F|G,
        "B": C|D|E|F|G,
        "C": A|D|E|F,
        "D": B|C|D|E|G,
        "E": A|D|E|F|G,
        "F": A|E|F|G,
        " ": 0,   # blank — all segments off
    }

    # --- Digit select bits ---
    # The display has 4 digit positions, each activated by a single bit.
    # This tells the shift register *which* digit position to light up.
    DIGITS = {
        0: 1<<0,
        1: 1<<1,
        2: 1<<2,
        3: 1<<3,
    }

    def __init__(self, shift_register, common_anode=True):
        self._sr = shift_register       # shift register used to send data to the display
        self._common_anode = common_anode
        self.current_text = " "         # 4-character string currently shown on the display
        self.counter = 0

    def segment_byte(self, char):
        # Look up the cathode pattern for char.
        # If the display is common-anode, invert all bits because on common-anode
        # a 0 turns a segment ON (the logic is flipped compared to common-cathode).
        char = char.upper()
        pattern = self.CATHODE_SEGMENTS.get(char, 0)
        if self._common_anode:
            pattern = ~pattern & 0xFF   # invert and mask to 8 bits
        return pattern

    def show_one_digit(self, digit_index, char):#shows one digit on the display
        # Build a 16-bit value to send to the shift register:
        #   high byte → which digit position to activate
        #   low byte  → which segments to light up
        digit_byte   = self.DIGITS[digit_index]#gets the digit byte
        segment_byte = self.segment_byte(char)#gets the segment byte
        value = (digit_byte << 8) | segment_byte#combines the digit byte and segment byte
        self._sr.shift_out_16bit(value)#shifts the data out to the shift register

    def refresh_once(self):#refreshes the display once
        # Multiplexing: only one digit is physically on at a time, but they cycle
        # through all 4 positions so fast (1 ms each) that the eye sees them all lit.
        for index, char in enumerate(self.current_text):#loops through each digit
            self.show_one_digit(index, char)#shows one digit on the display
            time.sleep(0.001)#pauses for the refresh delay

    def putValue(self, text, align="RIGHT"):#puts a value on the display
        # Store text (max 4 chars) in current_text, padded with spaces to fill 4 positions.
        text = str(text).upper()[:4]#stores the text
        if align == "LEFT":#checks the alignment
            self.current_text = text.ljust(4)#puts the text on the display
        else:#if the alignment is not left
            self.current_text = text.rjust(4)#puts the text on the display

    def putFilledValue(self, text, fill_char="0", align="RIGHT"):#puts a value on the display
        # Like putValue but uses a custom fill character instead of spaces,
        # e.g. fill_char="0" turns "42" into "0042".
        text = str(text).upper()[:4]#stores the text
        if align == "LEFT":#checks the alignment
            self.current_text = text.ljust(4, fill_char)#puts the text on the display
        else:#if the alignment is not left
            self.current_text = text.rjust(4, fill_char)#puts the text on the display

    def setCounter(self, value, align="RIGHT"):#sets the counter to a given value
        # Set the counter to a given value and update the display immediately.
        self.counter = int(value)#sets the counter
        self.putFilledValue(str(self.counter), fill_char="0", align="right")#puts the counter on the display

    def increment(self):#increments the counter
        # Add 1 to the counter and refresh the display.
        self.counter += 1#increments the counter
        self.putFilledValue(str(self.counter), fill_char="0", align="right")#puts the counter on the display

    def decrement(self):#decrements the counter
        # Subtract 1 from the counter and refresh the display.
        self.counter -= 1#decrements the counter
        self.putFilledValue(str(self.counter), fill_char="0", align="right")#puts the counter on the display
        
        
        