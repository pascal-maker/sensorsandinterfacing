from RPi import GPIO

class ShiftRegister:


  def __init__(self, data_pin:int = 22, latch_pin:int = 27, clock_pin:int = 17) -> None:
    self.dp = data_pin
    self.lp = latch_pin
    self.cp = clock_pin

    # setup pins
    self.setup()

  def setup(self):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(self.dp, GPIO.OUT)
    GPIO.setup(self.lp, GPIO.OUT)
    GPIO.setup(self.cp, GPIO.OUT)
    # setting clock and latch pins to low initially
    GPIO.output(self.lp, GPIO.LOW)
    GPIO.output(self.cp, GPIO.LOW)

  # Clock low/high
  def pulse_clock(self):
    GPIO.output(self.cp, GPIO.HIGH)
    GPIO.output(self.cp, GPIO.LOW)

  # Latch low/high
  def latch(self):
    GPIO.output(self.lp, GPIO.HIGH)
    GPIO.output(self.lp, GPIO.LOW)
  # Writing biytes
  def write_byte(self, value):
    mask = 0x80
    for _ in range(8):

      # looking at the most significant bit
      msb = value & mask

      # set datapin to HIGH if the most significant bit = 1
      if msb == 0x80:
        GPIO.output(self.dp, GPIO.HIGH)

      # set datapin to LOW if the most significant bit = 0
      else:
        GPIO.output(self.dp, GPIO.LOW)
      self.pulse_clock()
      value = value << 1
  # Writing bits
  def write_bit(self, bit):
    if bit == 1:
      GPIO.output(self.dp, GPIO.LOW)
    else:
      GPIO.output(self.dp, GPIO.HIGH)
    self.pulse_clock()
  # Shifting
  def shift_out_16_bits(self, bits, order:bool=True):
    byte1 = bits & 0xff
    byte2 = (bits >> 8) & 0xff
    if order:
      self.write_byte(byte2)
      self.write_byte(byte1)
      self.latch()
    else:
      self.write_byte(byte1)
      self.write_byte(byte2)
      self.latch()

