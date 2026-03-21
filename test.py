from smbus2 import SMBus
bus = SMBus(1)
bus.write_byte_data(0x68, 0x6B, 0x01) 
print("Wake up the MPU-6050")