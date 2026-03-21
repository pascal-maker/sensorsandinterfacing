import serial
ser = serial.Serial('/dev/ttyAMA0')
print(ser.name)
ser.write(b'hello')
ser.close()