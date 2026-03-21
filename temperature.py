from smbus2 import SMBus
import time
MPU_ADDRESS = 0x68
PWR_MGTM_1 = 0x6B
TEMP_OUT_H = 0x41


def combine_bytes(msb,lsb):
    value = (msb << 8) | lsb
    if value >= 0x8000:
        value -= 65536
    return value

bus = SMBus(1)
bus.write_byte_data(MPU_ADDRESS, PWR_MGTM_1, 0x01) 

while True:
    data = bus.read_i2c_block_data(MPU_ADDRESS, TEMP_OUT_H, 2)
    raw_temp = combine_bytes(data[0], data[1])
    temperature_c = raw_temp / 340.0 + 36.53
    print(f"Temperature: {temperature_c:.2f} °C")       
    print(f"Temperature raw: {raw_temp} (raw)")
    time.sleep(1)
    
    
    

