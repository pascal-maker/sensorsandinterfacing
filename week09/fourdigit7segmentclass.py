import time

class FourDigit7Segment:#a class that controls the four digit 7 segment display
    A = 1<<0#the segment bits
    B = 1<<1#the segment bits
    C = 1<<2#the segment bits
    D = 1<<3#the segment bits
    E = 1<<4#the segment bits
    F = 1<<5#the segment bits
    G = 1<<6#the segment bits
    DP = 1<<7#the segment bits

    CATHODE_SEGMENTS = {#the segment bits for each digit on common cathode
        0: A|B|C|D|E|F,#the segment bits
        1: B|C,#the segment bits
        2: A|B|D|E|G,#the segment bits
        3: A|B|C|D|G,#the segment bits
        4: B|C|F|G,#the segment bits
        5: A|C|D|F|G,#the segment bits
        6: A|C|D|E|F|G,#the segment bits
        7: A|B|C,#the segment bits
        8: A|B|C|D|E|F|G,#the segment bits
        9: A|B|C|D|F|G,#the segment bits
        "A": A|B|C|E|F|G,#the segment bits
        "B": C|D|E|F|G,#the segment bits
        "C": A|D|E|F,#the segment bits
        "D": B|C|D|E|G,#the segment bits
        "E": A|D|E|F|G,#the segment bits
        "F": A|E|F|G,
        " " : 0,#the segment bits
        
        
    }

    DIGITS = {#the digit bits
        0:1 <<0,#the digit bits
        1:1 << 1,#the digit bits
        2:1 << 2,#the digit bits
        3:1 << 3,#the digit bits
    }

    def __init__(self,shift_register,common_anode=True):#initializes the four digit 7 segment display
        self._sr = shift_register#the shift register to control the display
        self._common_anode = common_anode#the type of display
        self.current_text = " "#the current text to display
        self.counter = 0#the counter for the display

    def segment_byte(self,char):#the segment byte for each digit
        char = char.upper()#converts the character to uppercase

        pattern = self.CATHODE_SEGMENTS.get(char,0)#gets the segment byte for each digit

        if self._common_anode:#checks if the display is common anode
            pattern = ~pattern & 0xFF#inverts the segment byte
        
        return pattern


    def show_one_digit(self,digit_index,char):#shows one digit on the display
        digit_byte = self.DIGITS[digit_index]#gets the digit byte for each digit
        segment_byte = self.segment_byte(char)#gets the segment byte for each digit

        value = (digit_byte << 8) | segment_byte
        self._sr.shift_out_16bit(value)#shifts the segment byte to the shift register

    def refresh_once(self):#refreshes the display once
        for index,char in enumerate(self.current_text):#iterates through the current text
            self.show_one_digit(index,char)     #shows one digit on the display
            time.sleep(0.001)#waits for 0.001 seconds


    def putValue(self,text,align="RIGHT"):#puts the value on the display
        text = str(text).upper()[:4]#converts the text to uppercase
        if align == "LEFT":#checks if the alignment is left
            self.current_text = text.ljust(4)#left aligns the text
        else: #if the alignment is right
            self.current_text = text.rjust(4)#right aligns the text
        

    def putFilledValue(self,text,fill_char="0",align="RIGHT"):#puts the value on the display
        text = str(text).upper() [:4]#converts the text to uppercase

        if align == "LEFT":#checks if the alignment is left
            self.current_text = text.ljust(4,fill_char)#left aligns the text
        else:#if the alignment is right
            self.current_text = text.rjust(4,fill_char)#right aligns the text


    def setCounter(self,value,align="RIGHT"):#sets the counter to the given value
        self.counter = int(value)#sets the counter to the given value
        self.putFilledValue(str(self.counter),fill_char="0",align="right")#puts the value on the display
    def increment(self):#increments the counter
       self.counter +=1#increments the counter
       self.putFilledValue(str(self.counter),fill_char="0",align="right")#puts the value on the display    
    def decrement(self):#decrements the counter
        self.counter -=1#decrements the counter
        self.putFilledValue(str(self.counter),fill_char="0",align="right")#puts the value on the display
        
        
        