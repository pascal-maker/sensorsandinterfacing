import smbus
import time

class MPU6050:
    # Register Map Addresses
    PWR_MGMT_1   = 0x6B  # Power Management register (used to wake up the sensor)
    ACCEL_CONFIG = 0x1C  # Accelerometer configuration (sets full-scale range)
    GYRO_CONFIG  = 0x1B  # Gyroscope configuration (sets full-scale range)

    # Data Registers
    ACCEL_XOUT_H = 0x3B  # Start register for Accelerometer data (X, Y, Z)
    TEMP_OUT_H   = 0x41  # Start register for Temperature data
    GYRO_XOUT_H  = 0x43  # Start register for Gyroscope data (X, Y, Z)

    def __init__(self, address=0x68):
        self.address = address
        # Initialize I2C bus 1 (standard for most Raspberry Pi models)
        self.bus = smbus.SMBus(1)

    def setup(self):
        # Wake up the MPU6050; it starts in sleep mode by default
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0)
        
        # Set Accelerometer range to ±2g (sensitivity 16384 LSB/g)
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0)
        
        # Set Gyroscope range to ±250 °/s (sensitivity 131 LSB/°/s)
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, 0)
        
        # Small delay to allow the sensor to stabilize
        time.sleep(0.1)

    @staticmethod
    def convert_bytes(msb, lsb):
        """Combines two 8-bit registers into one 16-bit signed integer."""
        value = (msb << 8) | lsb
        # Handle two's complement for negative values
        if value & 0x8000:
            value -= 65536
        return value

    def read_temperature(self):
        """Reads and converts raw temperature to Celsius."""
        # Read 2 bytes (High and Low) starting from TEMP_OUT_H
        data = self.bus.read_i2c_block_data(self.address, self.TEMP_OUT_H, 2)
        raw_temp = self.convert_bytes(data[0], data[1])
        
        # Formula from MPU-6050 Register Map: (Raw / 340) + 36.53
        return raw_temp / 340.0 + 36.53

    def read_accel(self):
        """Reads 3-axis accelerometer data and returns g-force values."""
        # Read 6 bytes (X_H, X_L, Y_H, Y_L, Z_H, Z_L)
        data = self.bus.read_i2c_block_data(self.address, self.ACCEL_XOUT_H, 6)

        # Convert raw values to Gs using the ±2g sensitivity factor (16384)
        x = self.convert_bytes(data[0], data[1]) / 16384.0
        y = self.convert_bytes(data[2], data[3]) / 16384.0
        z = self.convert_bytes(data[4], data[5]) / 16384.0

        return x, y, z

    def read_gyro(self):
        """Reads 3-axis gyroscope data and returns degrees per second."""
        # Read 6 bytes (X_H, X_L, Y_H, Y_L, Z_H, Z_L)
        data = self.bus.read_i2c_block_data(self.address, self.GYRO_XOUT_H, 6)

        # Convert raw values to °/s using the ±250°/s sensitivity factor (131)
        x = self.convert_bytes(data[0], data[1]) / 131.0
        y = self.convert_bytes(data[2], data[3]) / 131.0
        z = self.convert_bytes(data[4], data[5]) / 131.0

        return x, y, z

# --- Main Execution ---
sensor = MPU6050()
sensor.setup()

try:
    while True:
        # Fetch data from sensor
        temp = sensor.read_temperature()
        ax, ay, az = sensor.read_accel()
        gx, gy, gz = sensor.read_gyro()

        # Print formatted output
        print("--- New Readings ---")
        print(f"Temperature: {temp:.2f} °C")
        print(f"Accelero: X: {ax:.2f}g, Y: {ay:.2f}g, Z: {az:.2f}g")
        print(f"Gyro:     X: {gx:.2f}°/s, Y: {gy:.2f}°/s, Z: {gz:.2f}°/s")
        print("-" * 20)

        # Wait 1 second before next poll
        time.sleep(1)

except KeyboardInterrupt:
    print("\nProgram stopped by user.")