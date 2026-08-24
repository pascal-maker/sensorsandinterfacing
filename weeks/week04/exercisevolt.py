import smbus#import smbus library
import time#import time library
i2c = smbus.SMBus(1)#set i2c bus
ADC_ADDRESS = 0x48#set i2c address

VREF = 3.3#set the maximum voltage measured by the ADC

commands_per_channel = { 2: 0x94 ,#the commands for the adc chip to read the voltage from the pots
                        3: 0xD4 ,#the commands for the adc chip to read the voltage from the pots
                        4: 0xA4  }#the commands for the adc chip to read the voltage from the pots
channel = 2#set the channel to read from
try:
    while True:#infinite loop to keep the program running
        i2c.write_byte(ADC_ADDRESS, commands_per_channel[channel])#write the command to the ADC
        i2c.read_byte(ADC_ADDRESS)#discard the previous conversion result
        data = i2c.read_byte(ADC_ADDRESS)#read the adc value return the value in 0-255 range
        voltage = data * VREF / 255#read the voltage from the ADC
        print(f"Channel {channel} -> ADC: {data:3d}, voltage: {voltage:.2f} V")#print the adc value and voltage
        time.sleep(0.2)#waits for 0.2 seconds
        
except KeyboardInterrupt:#if the user presses ctrl+c
    print("Program stopped")
finally:#always close the I2C bus, including when another error occurs
    i2c.close()

