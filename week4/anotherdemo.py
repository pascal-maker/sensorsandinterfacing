import smbus
import time

# Open I2C bus 1
i2c = smbus.SMBus(1)

# I2C address of ADC
ADC_ADDRESS = 0x48

# Commands for the channels
# A2 = channel 2
# A3 = channel 3
# A4 = channel 4
commands_per_channel = {
    2: 0b1001,
    3: 0b1101,
    4: 0b1011
}

# Choose the channel you want to read
channel = 4   # A4

while True:
    # Send command to ADC
    command = (commands_per_channel[channel] << 4) | 0x84 #commands_per_channel[channel] = which input
    #<< 4 = put it in the right position
    #| 0x84 = add required settings
    #write_byte(...) = send it to the ADC
    i2c.write_byte(ADC_ADDRESS, command)

    # Read 1 byte back (0-255)
    data = i2c.read_byte(ADC_ADDRESS)

    # Convert digital value to voltage
    voltage = data * 5.0 / 255

    # Print result
    print(f"Digital value: {data:3d}   Voltage: {voltage:.2f} V")

    time.sleep(0.5)