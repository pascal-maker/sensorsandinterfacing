import smbus
import time

class MPU6050:#define a class for mpu6050
    #constructor of the class mpu6050
    def __init__(self,address=0x68): #constructor is a special method that is called automatically when an object is created
        self.address = address #address of the mpu6050 sensor
        self.bus = smbus.SMBus(1) #initialize the i2c bus

   
    def setup(self):#setup method to configure the sensor
    #wake up the sensor
        self.bus.write_byte_data(self.address, 0x6B, 0) #wake up the sensor
    
       #accelerometer configuration
        self.bus.write_byte_data(self.address, 0x1C, 0) #set accelerometer range to +-2g

    #gyroscope configuration
        self.bus.write_byte_data(self.address, 0x1B, 0) #set gyroscope range to +-250dps
       
    @staticmethod #is a decorator that allows you to use a method as a standalone function
    def combine(high, low):#combine high and low bytes to get 16 bit value
        val = (high << 8) | low #shift high byte left by 8 and bitwise OR with low byte                                                                    
        #The << 8 just means "slide the high byte 8 positions to the left  
        #to make room for the low byte", then | slots the low byte in
        if val > 32767:#if value is greater than 32767, it is a negative number
            val -= 65536 #subtract 2^16 to get the negative value   #The if val > 32767: val -= 65536 part handles negative numbers — the sensor uses negative values for the
            #opposite direction (e.g. tilting left vs right). Without this, -1 would come out as 65535, so you subtract
            #65536 to get the correct negative number back.
        return val   
    # ============================================================
    # HOW _read_accel() AND _read_gyro() WORK — BEGINNER GUIDE
    # ============================================================
    #
    # BIG PICTURE:
    #   raw bytes → combine → fix sign → divide by scale → real value
    #
    # ------------------------------------------------------------
    # STEP 1: READ 6 BYTES FROM SENSOR
    # ------------------------------------------------------------
    #   data = bus.read_i2c_block_data(address, 0x3B, 6)
    #
    #   Why 6 bytes?
    #     X = 2 bytes (high + low)
    #     Y = 2 bytes
    #     Z = 2 bytes
    #     Total: 3 axes x 2 bytes = 6 bytes
    #
    #   Example of what sensor sends:
    #     data = [0x01, 0xF4, 0xFF, 0x9C, 0x40, 0x00]
    #              X_hi  X_lo  Y_hi  Y_lo  Z_hi  Z_lo
    #
    # ------------------------------------------------------------
    # STEP 2: COMBINE HIGH + LOW BYTES INTO ONE NUMBER
    # ------------------------------------------------------------
    #   x = combine(data[0], data[1])
    #   y = combine(data[2], data[3])
    #   z = combine(data[4], data[5])
    #
    #   Inside combine():
    #     val = (high << 8) | low
    #
    #   Example:
    #     high = 0x01 = 00000001
    #     low  = 0xF4 = 11110100
    #
    #     shift:  00000001 → 00000001 00000000
    #     OR:     00000001 00000000
    #           | 00000000 11110100
    #           = 00000001 11110100 = 500
    #
    #   So X raw = 500
    #
    # ------------------------------------------------------------
    # STEP 3: FIX NEGATIVE NUMBERS (2's complement)
    # ------------------------------------------------------------
    #   if val > 32767:
    #       val -= 65536
    #
    #   The sensor range is -32768 to +32767.
    #   Values above 32767 are actually negative:
    #     65535 - 65536 = -1   (65535 means -1)
    #
    # ------------------------------------------------------------
    # STEP 4: DIVIDE BY SCALE TO GET REAL UNITS
    # ------------------------------------------------------------
    #   ACCELEROMETER (±2g range):
    #     scale = 16384
    #     raw 16384 / 16384 = 1.0g  (gravity)
    #     bytes → combine → signed → ÷16384 → g
    #
    #   GYROSCOPE (±250dps range):
    #     scale = 131
    #     raw 131 / 131 = 1.0 degree per second
    #     bytes → combine → signed → ÷131 → °/s
    #
    # ------------------------------------------------------------
    # STEP 5: RETURN x, y, z IN REAL UNITS
    # ------------------------------------------------------------
    #   Sensor flat on table:
    #     Z ≈ 1g  (gravity pulling down)
    #     X ≈ 0
    #     Y ≈ 0
    #
    # ONE-LINE SUMMARY:
    #   Read 6 bytes, combine high+low pairs into 16-bit signed
    #   values, divide by scale factor to get real-world units.
    # ============================================================
    def _read_accel(self):#read acceleration data
        data = self.bus.read_i2c_block_data(self.address, 0x3B, 6)#read 6 bytes starting from 0x3B reading 6 bytes at once grabs all accelerometer data in one shot reducing delay and error the MPU6050 stor3s each axis value as a 16-bit signed integer split across 2 bytes (high byte + low byte). there are 3 axes, so 3 axes x 2 bytes = 6 bytes total
        x = self.combine(data[0], data[1])#convert raw acceleration to g how much force the sensor feels relative to gravity in each direction  dividing by 16834 convers the raw number into a scale of -1 to 1 
        y = self.combine(data[2], data[3])#convert raw acceleration to g
        z = self.combine(data[4], data[5])#convert raw acceleration to g
        
        #convert to g
        x = x / 16384.0 #convert raw number into a scale of -1 to 1 
        y = y / 16384.0 #convert raw number into a scale of -1 to 1 
        z = z / 16384.0 #convert raw number into a scale of -1 to 1 
        return x, y, z    #return x, y, z acceleration values

    def _read_gyro(self):#read gyroscope data
        data = self.bus.read_i2c_block_data(self.address, 0x43, 6)#read 6 bytes starting from 0x43 reading 6 bytes at once grabs all gyroscope data in one shot reducing delay and error
        x = self.combine(data[0], data[1])#convert raw gyroscope to degrees per second how fast the sensor is rotating
        y = self.combine(data[2], data[3])#convert raw gyroscope to degrees per second
        z = self.combine(data[4], data[5])  #convert raw gyroscope to degrees per second
        #                                                                                           
        #combine(data[2], data[3]) → full Y value                                                                    
        #combine(data[4], data[5]) → full Z value
        #                                          
        #  Text 1: "0207"      ← data[0] (high byte)
        #Text 2: "496120"    ← data[1] (low byte)                                                                      
        #combine → "0207496120"  ← the actual number                                                                   
        #The sensor had one 16-bit number for X, couldn't send it whole, so it sent the first half in data[0] and the  
        #second half in data[1]. combine just puts them back together.
        #convert to dps
        x = x / 131.0#convert raw number into a scale of -250 to 250 degrees per second 
        y = y / 131.0#convert raw number into a scale of -250 to 250 degrees per second 
        z = z / 131.0#convert raw number into a scale of -250 to 250 degrees per second 
        return x, y, z  #return x, y, z gyroscope values
    
    def get_acceleration(self):#get acceleration data
        return self._read_accel()
    
    def get_gyroscope(self):#get gyroscope data
        return self._read_gyro()
mpu = MPU6050()#create an object of the MPU6050 class
mpu.setup()#setup the sensor

while True:
   ax,ay,az = mpu.get_acceleration()#get acceleration data
   gx,gy,gz = mpu.get_gyroscope()#get gyroscope data
   print(f"Acceleration: {ax}, {ay}, {az}")#print acceleration data
   print(f"Gyroscope: {gx}, {gy}, {gz}")#print gyroscope data
   time.sleep(0.05)  #wait for 0.05 seconds
