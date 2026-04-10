import smbus
import time


class MPU6050:
    PWR_MGMT_1 = 0x6B
    ACCEL_CONFIG = 0x1C
    GYRO_CONFIG = 0x1B

    ACCEL_XOUT_H = 0x3B
    TEMP_OUT_H = 0x41
    GYRO_XOUT_H = 0x43

    def __init__(self, address=0x68):
        self.address = address
        self.bus = smbus.SMBus(1)

    def setup(self):
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0)
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0)  # ±2g
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, 0)   # ±250°/s
        time.sleep(0.1)

    @staticmethod
    def convert_bytes(msb, lsb):
        value = (msb << 8) | lsb
        if value & 0x8000:
            value -= 65536
        return value

    def read_temperature(self):
        data = self.bus.read_i2c_block_data(self.address, self.TEMP_OUT_H, 2)
        raw_temp = self.convert_bytes(data[0], data[1])
        return raw_temp / 340.0 + 36.53

    def read_accel(self):
        data = self.bus.read_i2c_block_data(self.address, self.ACCEL_XOUT_H, 6)

        x = self.convert_bytes(data[0], data[1]) / 16384.0
        y = self.convert_bytes(data[2], data[3]) / 16384.0
        z = self.convert_bytes(data[4], data[5]) / 16384.0

        return x, y, z

    def read_gyro(self):
        data = self.bus.read_i2c_block_data(self.address, self.GYRO_XOUT_H, 6)

        x = self.convert_bytes(data[0], data[1]) / 131.0
        y = self.convert_bytes(data[2], data[3]) / 131.0
        z = self.convert_bytes(data[4], data[5]) / 131.0

        return x, y, z


sensor = MPU6050()
sensor.setup()

while True:
    temp = sensor.read_temperature()
    ax, ay, az = sensor.read_accel()
    gx, gy, gz = sensor.read_gyro()

    print("new readings")
    print(f"temperature is {temp:.2f} Celsius")
    print(f"accelero : x : {ax:.2f}   y : {ay:.2f}   z : {az:.2f}")
    print(f"gyro : rot_x : {gx:.2f}°/s   rot_y : {gy:.2f}°/s   rot_z : {gz:.2f}°/s")
    print()

    time.sleep(1)