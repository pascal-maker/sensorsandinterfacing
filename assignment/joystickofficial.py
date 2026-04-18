#!/usr/bin/env python3
import smbus
import time

ADC_ADDRESS = 0x48

X_CHANNEL = 5
Y_CHANNEL = 6

X_NEUTRAL = 127
Y_NEUTRAL = 131
DEADZONE = 25

def ads7830_command(channel):
    return 0x84 | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)

def read_adc(bus, channel):
    cmd = ads7830_command(channel)
    bus.write_byte(ADC_ADDRESS, cmd)
    time.sleep(0.01)
    return bus.read_byte(ADC_ADDRESS)

def get_x_position(value):
    if value < X_NEUTRAL - DEADZONE:
        return "RIGHT"
    elif value > X_NEUTRAL + DEADZONE:
        return "LEFT"
    else:
        return "CENTER"

def get_y_position(value):
    if value < Y_NEUTRAL - DEADZONE:
        return "DOWN"
    elif value > Y_NEUTRAL + DEADZONE:
        return "UP"
    else:
        return "CENTER"

bus = smbus.SMBus(1)
print("[ADC] ADC found at 0x48")

try:
    while True:
        x_val = read_adc(bus, X_CHANNEL)
        y_val = read_adc(bus, Y_CHANNEL)

        x_pos = get_x_position(x_val)
        y_pos = get_y_position(y_val)

        print(f"X: {x_val:3d} ({x_pos}) | Y: {y_val:3d} ({y_pos})")
        time.sleep(0.2)

except KeyboardInterrupt:
    bus.close()
    print("\nStopped")