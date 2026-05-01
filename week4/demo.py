import smbus
import time 
bus = smbus.SMBus(1) #set the i2c bus
address = 0x48 #set the address 

VREF = 3.3 #reference voltage

def read_adc(channel):#function to read the ADC channel
    command = 0x84 | ((channel & 0x07) << 4)#<< 4 put it in the right position command 0x84 sets the single-ended inut mode and start bit for the PCF8591 ADC mask to 3 bits chabbel 0-7 <<4 shifts the channel number into bits 4-6 of command byte
    # | 0x84 = add required settings
    bus.write_byte(address, command)  # send channel select command to ADC
    value = bus.read_byte(address)    # read the converted value
    return value#return the data

try:
    while True:
        ch = 2#choose the ADC channel
        value = read_adc(ch) # Read the value from the ADC
        voltage = (value /255 )* VREF #convert the ADC value to voltage values range 0-255 dvididng by 255 results 0.0 -1.0 multiplying by vref scales to actual voltage value
        print(f" Channel {ch} value={value} voltage={voltage:.2f}")#print the data
        time.sleep(0.5)#wait for 0.5 seconds
except KeyboardInterrupt:
    print("Exiting")
finally:
    bus.close()
