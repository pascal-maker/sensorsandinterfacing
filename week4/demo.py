import smbus
import time

# Use I²C bus 1 on the Raspberry Pi
I2C_BUS = 1

# I²C address of the ADS7830 ADC chip
ADS7830_ADDR = 0x48

# Open the I²C bus so Python can talk to the ADC
bus = smbus.SMBus(I2C_BUS)

# Function to read one channel from the ADS7830
def read_ads7830(command):
    # Send the command byte to the ADC and read back 1 byte (0..255)
    value = bus.read_byte_data(ADS7830_ADDR, command)

    # Convert the ADC value into a voltage between 0V and 3.3V
    voltage = value * 3.3 / 255

    # Give back both the raw ADC value and the calculated voltage
    return value, voltage

try:
    while True:
        # Read channel 2 using command byte 0x94
        value, voltage = read_ads7830(0x94)

        # Print the raw ADC number and the converted voltage
        print(f"Channel 2 -> ADC: {value:3d}, Voltage: {voltage:.2f} V")

        # Wait a little before reading again
        time.sleep(0.2)

# Stop the program safely when Ctrl+C is pressed
except KeyboardInterrupt:
    bus.close()