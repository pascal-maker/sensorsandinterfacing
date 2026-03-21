from smbus2 import SMBus
import time 

class MPU6050:
    PWR_MGMT_1 = 0x6B
    ACCEL_CONFIG = 0x1C
    GYRO_CONFIG = 0x1B
    ACCEL_XOUT_H = 0x3B
    TEMP_OUT_H = 0x41
    GYRO_XOUT_H = 0x43
    
    ACCEL_RANGE = {2: 0x00, 4: 0x08, 8: 0x10, 16: 0x18}
    GYRO_RANGE = {250: 0x00, 500: 0x08, 1000: 0x10, 2000: 0x18}
    ACCEL_SCALE = {2: 16384.0, 4: 8192.0, 8: 4096.0, 16: 2048.0}
    GYRO_SCALE = {250: 131.0, 500: 65.5, 1000: 32.8, 2000: 16.4}

    def __init__(self, address, bus_num=1, accel_range=2, gyro_range=250):
        self.address = address
        self.bus = SMBus(bus_num)
        self.accel_range = accel_range
        self.gyro_range = gyro_range
    
    def setup(self):
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x01) 
        
        self.bus.write_byte_data(
            self.address,
            self.ACCEL_CONFIG,
            self.ACCEL_RANGE[self.accel_range]
        )

        self.bus.write_byte_data(
            self.address,
            self.GYRO_CONFIG,
            self.GYRO_RANGE[self.gyro_range]
        )
        
        time.sleep(0.1)
        
    @staticmethod
    def combine_bytes(msb, lsb):
        value = (msb << 8) | lsb
        if value >= 0x8000:
            value -= 65536
        return value
    
    def _read_accel_data(self):
        data = self.bus.read_i2c_block_data(self.address, self.ACCEL_XOUT_H, 6)
        raw_x = self.combine_bytes(data[0], data[1])
        raw_y = self.combine_bytes(data[2], data[3])
        raw_z = self.combine_bytes(data[4], data[5])

        scale = self.ACCEL_SCALE[self.accel_range]
        
        x_g = raw_x / scale
        y_g = raw_y / scale
        z_g = raw_z / scale
        return x_g, y_g, z_g

    def _read_gyro_data(self):
        data = self.bus.read_i2c_block_data(self.address, self.GYRO_XOUT_H, 6)
        raw_x = self.combine_bytes(data[0], data[1])
        raw_y = self.combine_bytes(data[2], data[3])
        raw_z = self.combine_bytes(data[4], data[5])

        scale = self.GYRO_SCALE[self.gyro_range]
        
        x_dps = raw_x / scale
        y_dps = raw_y / scale
        z_dps = raw_z / scale
        return x_dps, y_dps, z_dps
    def _read_temperature(self):
        data = self.bus.read_i2c_block_data(self.address, self.TEMP_OUT_H, 2)
        raw_temp = self.combine_bytes(data[0], data[1])
        temp_c = (raw_temp / 340.0) + 36.53
        return temp_c
    
    def get_acceleration(self):
        return self._read_accel_data()
    
    def get_gyroscope(self):
        return self._read_gyro_data()
    
    def get_temperature(self):
        return self._read_temperature()
    
 

if __name__ == "__main__":
    mpu = MPU6050(0x68, accel_range=2, gyro_range=250)
    mpu.setup()
    
    while True:
        accel = mpu.get_acceleration()
        gyro = mpu.get_gyroscope()
        temp = mpu.get_temperature()
        print(f"Temperature (C): {temp:.2f}")
        print(f"Acceleration (g): X={accel[0]:.2f}, Y={accel[1]:.2f}, Z={accel[2]:.2f}")
        print(f"Gyroscope (°/s): X={gyro[0]:.2f}, Y={gyro[1]:.2f}, Z={gyro[2]:.2f}")
        time.sleep(1)