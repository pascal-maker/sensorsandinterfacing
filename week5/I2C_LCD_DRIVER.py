import smbus
import time

ADDRESS = 0x27

LCD_CLEARDISPLAY    = 0x01
LCD_RETURNHOME      = 0x02
LCD_ENTRYMODESET    = 0x04
LCD_DISPLAYCONTROL  = 0x08
LCD_FUNCTIONSET     = 0x20
LCD_DISPLAYON       = 0x04
LCD_2LINE           = 0x08
LCD_5x8DOTS         = 0x00
LCD_4BITMODE        = 0x00
LCD_ENTRYLEFT       = 0x02
LCD_BACKLIGHT       = 0x08
En                  = 0x04
Rs                  = 0x01

class lcd:
    def __init__(self):
        self.bus = smbus.SMBus(1)
        self.addr = ADDRESS
        for _ in range(3):
            self._write4(0x30)
        self._write4(0x20)
        self._cmd(LCD_FUNCTIONSET | LCD_2LINE | LCD_5x8DOTS | LCD_4BITMODE)
        self._cmd(LCD_DISPLAYCONTROL | LCD_DISPLAYON)
        self._cmd(LCD_CLEARDISPLAY)
        self._cmd(LCD_ENTRYMODESET | LCD_ENTRYLEFT)
        time.sleep(0.2)

    def _strobe(self, data):
        self.bus.write_byte(self.addr, data | En | LCD_BACKLIGHT)
        time.sleep(0.0005)
        self.bus.write_byte(self.addr, (data & ~En) | LCD_BACKLIGHT)
        time.sleep(0.0001)

    def _write4(self, data):
        self.bus.write_byte(self.addr, data | LCD_BACKLIGHT)
        self._strobe(data)

    def _cmd(self, cmd, mode=0):
        self._write4(mode | (cmd & 0xF0))
        self._write4(mode | ((cmd << 4) & 0xF0))

    def lcd_display_string(self, string, line):
        line_offsets = {1: 0x80, 2: 0xC0, 3: 0x94, 4: 0xD4}
        self._cmd(line_offsets.get(line, 0x80))
        for char in string:
            self._cmd(ord(char), Rs)

    def lcd_clear(self):
        self._cmd(LCD_CLEARDISPLAY)
        self._cmd(LCD_RETURNHOME)
