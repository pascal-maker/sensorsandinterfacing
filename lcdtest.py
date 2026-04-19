#!/usr/bin/env python3
import smbus
import time

I2C_ADDR = 0x27
LCD_WIDTH = 16

LCD_CHR = 1
LCD_CMD = 0

LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0

ENABLE = 0b00000100
RS = 0b00000001

bus = smbus.SMBus(1)

def lcd_toggle_enable(bits):
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, bits | ENABLE)
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)
    time.sleep(0.0005)

def lcd_send_byte(bits, mode):
    high_bits = mode | (bits & 0xF0) | 0x08
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08

    bus.write_byte(I2C_ADDR, high_bits)
    lcd_toggle_enable(high_bits)

    bus.write_byte(I2C_ADDR, low_bits)
    lcd_toggle_enable(low_bits)

def lcd_init():
    lcd_send_byte(0x33, LCD_CMD)
    lcd_send_byte(0x32, LCD_CMD)
    lcd_send_byte(0x06, LCD_CMD)
    lcd_send_byte(0x0C, LCD_CMD)
    lcd_send_byte(0x28, LCD_CMD)
    lcd_send_byte(0x01, LCD_CMD)
    time.sleep(0.005)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_send_byte(line, LCD_CMD)

    for i in range(LCD_WIDTH):
        lcd_send_byte(ord(message[i]), LCD_CHR)

lcd_init()

try:
    lcd_string("Hello Pascal", LCD_LINE_1)
    lcd_string("LCD works", LCD_LINE_2)
    time.sleep(3)

    lcd_send_byte(0x01, LCD_CMD)
    lcd_string("Line 1 test", LCD_LINE_1)
    lcd_string("Line 2 test", LCD_LINE_2)
    time.sleep(3)

    lcd_send_byte(0x01, LCD_CMD)

except KeyboardInterrupt:
    lcd_send_byte(0x01, LCD_CMD)
    print("Stopped")