import smbus
import time
class MPU6050:
    def __init__(self,address=0x68):#constructor is a special method that is called automatically when an object is created
        self.address = address#address of the mpu6050 sensor
        self.bus = smbus.SMBus(1)#initialize the i2c bus

        self._accel_range = 0#0:+2g, 1:+-4g, 2:+-8g, 3:+16g#accelerometer range
        self ._gyro_range = 0#0:+250dps, 1:+500dps, 2:+1000dps, 3:+2000dps#gyroscope range
        self._accel_scale = 16384.0#scale factor for each accel range#
        self._gyro_scale = 131.0#scale factor for each gyro range
    
    # ============================================================
    # HOW THE RANGE SYSTEM WORKS — BEGINNER GUIDE
    # ============================================================
    #
    # WHY DO WE NEED A RANGE?
    #   The sensor can measure different amounts of movement.
    #   A small range (±2g) is more precise for slow movement.
    #   A big range (±16g) can measure fast/violent movement
    #   but with less precision. You pick based on your use case.
    #
    # ------------------------------------------------------------
    # STEP 1: DEFAULTS SET IN __init__
    # ------------------------------------------------------------
    #   self._accel_range = 0   → 0 means ±2g
    #   self._gyro_range  = 0   → 0 means ±250dps
    #   self._accel_scale = 16384.0  → matching scale for ±2g
    #   self._gyro_scale  = 131.0   → matching scale for ±250dps
    #
    #   Nothing is sent to the sensor yet. Just storing defaults.
    #
    # ------------------------------------------------------------
    # STEP 2: setup() IS CALLED
    # ------------------------------------------------------------
    #   setup() wakes the sensor, then calls _apply_ranges()
    #   to actually write the range settings to the sensor.
    #
    # ------------------------------------------------------------
    # STEP 3: _apply_ranges() DOES TWO THINGS
    # ------------------------------------------------------------
    #
    #   THING 1 — Tell the sensor hardware what range to use:
    #     bus.write_byte_data(address, 0x1C, accel_range << 3)
    #
    #     The << 3 shifts your range value into bits 3 and 4
    #     of the register (that is where the sensor expects it):
    #       range=0 → 0<<3 = 00000000 → ±2g
    #       range=1 → 1<<3 = 00001000 → ±4g
    #       range=2 → 2<<3 = 00010000 → ±8g
    #       range=3 → 3<<3 = 00011000 → ±16g
    #
    #   THING 2 — Pick the matching scale factor for our math:
    #     accel_scales = [16384.0, 8192.0, 4096.0, 2048.0]
    #                      ±2g      ±4g     ±8g     ±16g
    #
    #     gyro_scales  = [131.0, 65.5, 32.8, 16.4]
    #                    ±250   ±500  ±1000 ±2000 dps
    #
    #   IMPORTANT: as range doubles, scale halves.
    #   Because the same 16-bit number now covers a bigger range,
    #   so each unit represents more movement.
    #
    #   These two MUST always match:
    #     sensor hardware range  ←→  scale factor in our math
    #   If they don't, readings will be wrong.
    #
    # ------------------------------------------------------------
    # STEP 4: CHANGING RANGE AT RUNTIME WITH THE SETTER
    # ------------------------------------------------------------
    #   mpu.range = (1, 0)   → accel ±4g, gyro ±250dps
    #
    #   The setter does:
    #     self._accel_range = 1
    #     self._gyro_range  = 0
    #     self._apply_ranges()   → re-writes registers + updates scale
    #
    #   Now _read_accel() divides by 8192.0 instead of 16384.0
    #   automatically. No other code needs to change.
    #
    # ------------------------------------------------------------
    # FULL FLOW:
    # ------------------------------------------------------------
    #   set range (0/1/2/3)
    #        ↓
    #   write range to sensor hardware registers
    #        ↓
    #   pick matching scale number from list
    #        ↓
    #   every read: raw number / scale = real world value
    #
    # ONE-LINE SUMMARY:
    #   Range tells the sensor how much movement to expect.
    #   Scale converts the raw number into real units (g or dps).
    #   They must always match or readings will be wrong.
    # ============================================================
    def setup(self):
        #wake up
        self.bus.write_byte_data(self.address, 0x6B, 0)#wake up the sensor
        self._apply_ranges()#  send range
    @property
    def range(self):
        return self._accel_range, self._gyro_range#return accel range
    @range.setter
    def range(self, values):#set range
        accel,gyro = values#set accel and gyro range
        self._accel_range = accel#set accel range means +2g
        self._gyro_range = gyro#set gyro range means +250dps
        self._apply_ranges()#apply ranges

    def _apply_ranges(self):
        #write to ranges
        self.bus.write_byte_data(self.address, 0x1C, self._accel_range << 3)#shift 3 bits left to set bits 3,4 for accel range tell sensor use +-2g pyschically writes to sensor use +- 2g mode and it changes its internal hardware to support the new range
        self.bus.write_byte_data(self.address, 0x1B, self._gyro_range << 3)#shift 3 bits left to set bits 3,4 for gyro range tell sensor use +-250dps pyschically writes to sensor use +-250dps and it changes its internal hardware to support the new range

        accel_scales =  [16384.0, 8192.0, 4096.0, 2048.0]#accel scale factors for each range then picks the matching scale factor they must alwys match up to the sensor range we pick 
        gyro_scales =  [131.0, 65.5, 32.8, 16.4]#gyro scale factors for each range pics the matching scal factor for our math these two must alwys match up to the sensor range we pick 

        self._accel_scale = accel_scales[self._accel_range]#set accel scale factor
        self._gyro_scale = gyro_scales[self._gyro_range]#set gyro scale factor
    @staticmethod
    def combine(high, low):#combine high and low bytes to get 16 bit value
        val = (high << 8) | low#shift high byte left by 8 and bitwise OR with low byte                                                                    
        #The << 8 just means "slide the high byte 8 positions to the left  
        #to make room for the low byte", then | slots the low byte in
        if val > 32767:#if value is greater than 32767, it is a negative number
            val -= 65536 #subtract 2^16 to get the negative value   #The if val > 32767: val -= 65536 part handles negative numbers — the sensor uses negative values for the
            #opposite direction (e.g. tilting left vs right). Without this, -1 would come out as 65535, so you subtract
            #65536 to get the correct negative number back.
        return val   
    def _read_accel(self):
        data = self.bus.read_i2c_block_data(self.address, 0x3B, 6)#read 6 bytes starting from 0x3B reading 6 bytes at once grabs all accelerometer data in one shot reducing delay and error the MPU6050 stor3s each axis value as a 16-bit signed integer split across 2 bytes (high byte + low byte). there are 3 axes, so 3 axes x 2 bytes = 6 bytes total
        x = self.combine(data[0], data[1])/self._accel_scale#convert raw acceleration to g how much force the sensor feels relative to gravity in each direction  dividing by 16834 convers the raw number into a scale of -1 to 1 
        y = self.combine(data[2], data[3])/self._accel_scale#convert raw acceleration to g
        z = self.combine(data[4], data[5])/self._accel_scale#convert raw acceleration to g
        return x, y, z    #return x, y, z acceleration values
    def _read_gyro(self):
        data = self.bus.read_i2c_block_data(self.address, 0x43, 6)#read 6 bytes starting from 0x43 reading 6 bytes at once grabs all gyroscope data in one shot reducing delay and error
        x = self.combine(data[0], data[1])/self._gyro_scale#convert raw gyroscope to degrees per second how fast the sensor is rotating
        y = self.combine(data[2], data[3])/self._gyro_scale#convert raw gyroscope to degrees per second
        z = self.combine(data[4], data[5])/self._gyro_scale  #convert raw gyroscope to degrees per second
        return x,y,z#return x, y, z gyroscope values

    def get_temperature(self):
        data = self.bus.read_i2c_block_data(self.address, 0x41, 2)#read 2 bytes starting from 0x41 reading 2 bytes at once grabs all temperature data in one shot reducing delay and error
        raw_temp = self.combine(data[0], data[1])#raw temperature data
        temp = raw_temp/340.0 + 36.53#convert raw temperature to celsius
        return temp    
    def get_acceleration(self):#get acceleration data
        return self._read_accel()
    def get_gyroscope(self):#get gyroscope data
        return self._read_gyro()
mpu = MPU6050()#create an object of the MPU6050 class
mpu.setup()#setup the sensor
mpu.range = (0, 0)#set range to +-2g and +-250dps

while True:
    ax, ay, az = mpu.get_acceleration()#get acceleration data
    gx, gy, gz = mpu.get_gyroscope()#get gyroscope data
    print(f"Temperature: {mpu.get_temperature():.2f} degrees Celsius")
    print(f"Acceleration: {ax:.2f} x-direction, {ay:.2f} y-direction, {az:.2f} z-direction")#print acceleration data
    print(f"Gyroscope: {gx:.2f} x-rotation, {gy:.2f} y-rotation, {gz:.2f} z-rotation")#print gyroscope data
    time.sleep(1)#wait for 1 seconds

