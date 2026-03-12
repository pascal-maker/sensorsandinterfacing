import smbus
import time
i2c = smbus.SMBus(1)
ADC_ADDRESS = 0x48

VREF = 5.0

commands_per_channel = { 2: 0x94 ,
                        3: 0xD4 ,
                        4: 0xA4  }
channel = 2 
try:
    while True:
        i2c.write_byte(ADC_ADDRESS, commands_per_channel[channel])
        data = i2c.read_byte(ADC_ADDRESS)
        voltage = data * VREF / 255
        print(f"Channel {channel} -> ADC: {data:3d}")
        time.sleep(0.2)
        
except KeyboardInterrupt:
    i2c.close()        


#What the script does

#opens the bus

#talks to the ADS7830 at address 0x48

#sends the correct command byte for A2, A3 or A4

#reads back one 8-bit value from 0 to 255

#converts that number into a voltage between 0 and 5V    