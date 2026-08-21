from ShiftRegister import ShiftRegister
from RPi import GPIO
from time import sleep

# y-coords for the Led Matrix
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
# Clearing matrix
def clear_matrix():
  try:
    shift_reg = ShiftRegister()
    clear_bits = [0x00] * 8
    for o in range(8):
      row_byte = 1 << o
      # We only need to write the row buffer once, not 8 duplicate times
      data_word = row_byte << 8 | (0xff & ~clear_bits[o])
      shift_reg.shift_out_16_bits(data_word)
      sleep(0.001)
  except KeyboardInterrupt:
    print("\nCleanup")

# clearing directly by running this file
def clear():
  shift_reg = ShiftRegister()
  shift_reg.shift_out_16_bits(0x00 << 8 | 0xff)

def test_matrix():
  shift_reg = ShiftRegister()
  # Light up all LEDs (assuming rows are active high, cols active low)
  # or test alternating pattern
  try:
    while True:
      # Alternating test to ensure it blinks properly no matter the wiring
      shift_reg.shift_out_16_bits(0xff00)
      sleep(0.5)
      shift_reg.shift_out_16_bits(0x00ff)
      sleep(0.5)
  except KeyboardInterrupt:
    clear()
  finally:
    GPIO.cleanup()

if __name__ == "__main__":
  test_matrix()