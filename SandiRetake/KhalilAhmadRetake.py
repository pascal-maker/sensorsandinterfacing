from RPi import GPIO
import csv
import os
from time import sleep, time
from ShiftRegister import ShiftRegister
import smbus
import threading
import copy

shift_reg = ShiftRegister()
i2c = smbus.SMBus(1)
GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# coords for the Led Matrix
y_coords = [
  0x01,
  0x02,
  0x04,
  0x08,
  0x10,
  0x20,
  0x40,
  0x80
]
x_coords = [
  0x0100,
  0x0200,
  0x0400,
  0x0800,
  0x1000,
  0x2000,
  0x4000,
  0x8000
]
# clearing Led Matrix
def clear_matrix():
  global shift_reg
  shift_reg.shift_out_16_bits(0x00 << 8 | 0xff)

matrix_state = True

# Switwching the matrix, on/off
def toggle_matrix(channel):
  global matrix_state
  matrix_state = not matrix_state

i = 0
list_patterns = []

# displaying the bars
def display(value):
  global i, x_coords, y_coords

  i+=1
  if i > 7:
    i = 0
  # putting limit to 8 patterns
  if len(list_patterns)>8:
    list_patterns.remove(list_patterns[0])
  pattern = 0
  for n in range(value):
    pattern |= y_coords[n]

  list_patterns.append(pattern)
# i2C 
ADC_address = 0x48
adc_channels = {
    0:0b1000,
    1:0b1000,
    2:0b1001,
    3:0b1101,
    4:0b1010,
    5:0b1110,
    6:0b1011
}
GPIO.add_event_detect(20, GPIO.FALLING, toggle_matrix, bouncetime=200)

# Reading values and updating matrix
def read_values():
  while True:
    # Stopping list size change in case of errors during iteration.
    list1 = copy.deepcopy(list_patterns)
    if matrix_state:
      o = 0
      for pattern in list1:
        if o==8: o=0
        bytes = x_coords[o] | (0xff & ~pattern)
        shift_reg.shift_out_16_bits(bytes)
        o+=1
    else:
      clear_matrix()
try:
  threading.Thread(target=read_values, daemon=True).start()
  
  csv_path = os.path.join(os.path.dirname(__file__), "PotentiometerInputs.csv")
  file_exists = os.path.exists(csv_path)
  with open(csv_path, "a", newline='') as csvfile:
    writer = csv.writer(csvfile)
    if not file_exists:
      writer.writerow(["Values"])
      print("CSV created")
    else:
      print("Adding")

    # reading adc values, writing on csv and displaying to matrix
    while True:
      if matrix_state:
        i2c.write_byte(ADC_address,(adc_channels[2] << 4) | 0x4)
        # Flush the buffer to ensure data is written out 
        csvfile.flush()
        writer.writerow([str(i2c.read_byte(ADC_address))])
        matrix_rep = round(i2c.read_byte(ADC_address)/255 * 8)
        display(matrix_rep)
      # Sleep needs to happen outside the if to avoid a tight infinite loop when matrix is off
      sleep(1)
      
except KeyboardInterrupt:
   print("\nCancelling")

finally:
  clear_matrix()
  GPIO.cleanup()
  print("Cleanup")