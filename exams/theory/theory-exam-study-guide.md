# Sensors & Interfacing — Exam Study Guide

## How to study (Feynman technique)
1. Read one section below
2. Close everything — explain it out loud to yourself like teaching a friend
3. Where you get stuck → ask Claude to explain just that part
4. Do the practice exercises without looking at answers
5. Verify in Python: `python3 -c "print(bin(0xFF & 0x0F))"`

---

## Study plan — full sequence

### Step 1: Read your own code out loud (one week per session)

Your repository code IS your study material. Go through each week in order:

| Week | File(s) to read | Exam topic it covers |
|------|----------------|---------------------|
| **week02** | toggle/edge detection | GPIO, digital signals |
| **week03** | bitwise operations | Bit operations (exam questions!) |
| **week04** | ADC / I2C | ADC, I2C bus, analog signals |
| **week05** | LCD, servo | I2C addressing, PWM |
| **week06** | MPU6050 | I2C, sensor data, data logging |
| **week07** | motors, BLE | protocols, wireless |
| **week08** | shift register | SPI-style serial, bit shifting |
| **week09** | multiplexing | LED matrix, timing |
| **week011** | RFID, camera, gestures | SPI, SPI vs I2C, OpenCV |

**Routine for each file:**
- Open it, read every line out loud
- For every function — explain what it does and WHY
- If a line uses `&`, `|`, `<<` — explain the bit operation out loud
- If a line uses `GPIO` — say which pin and why
- Start with **week03** — bit operations are guaranteed on the exam

---

### Step 2: Do the exam exercises from the PDF
- Solve Ex 1 and Ex 2 without looking at answers
- Then verify in Python: `python3 -c "..."`
- Make up 3 similar ones yourself and solve them

---

### Step 3: Memorize the pin table
- Cover the pin table in this file with your hand
- Recite out loud: "I2C is GPIO 2 and 3, SPI MOSI is GPIO 10..."
- Repeat until instant recall, no hesitation

---

### Step 4: Practice the practical exam setup
- Plug in your USB with all your code
- Practice navigating and copying files fast
- Run each script to make sure it still works
- Time yourself — don't waste time on file navigation on exam day

---

### Step 5: One mock exam session
- Ask Claude for 5 random bit operation questions
- Answer them on paper, no Python
- Then verify every answer in Python
- Repeat until you get them all right first try

---

## 1. Bit Operations (always on the exam)

### The 4 operators
| Operator | Symbol | Use case |
|----------|--------|----------|
| AND | `&` | Extract bits (mask off what you don't want) |
| OR | `\|` | Combine bits from two sources |
| XOR | `^` | Toggle/flip specific bits |
| Shift | `<<` `>>` | Move bits to a different position |

### Common masks
| Mask | Binary | Use |
|------|--------|-----|
| `0x0F` | `0000 1111` | Keep low nibble (bits 0-3) |
| `0xF0` | `1111 0000` | Keep high nibble (bits 4-7) |
| `0xFF` | `1111 1111` | Keep full byte |

### Recipe: Extract bits
```python
# Extract low nibble of X
low = X & 0x0F

# Extract high nibble of X (shift it down to position 0-3)
high = (X & 0xF0) >> 4

# Extract bit 6 only
bit6 = (X >> 6) & 1
```

### Recipe: Combine bits from two bytes
```python
# X1 = B7 B6 B5 B4 | A7 A6 A5 A4
# X2 = B3 B2 B1 B0 | A3 A2 A1 A0

A = ((X1 & 0x0F) << 4) | (X2 & 0x0F)   # low nibbles → one byte
B = (X1 & 0xF0) | ((X2 & 0xF0) >> 4)   # high nibbles → one byte
```

### Recipe: Toggle a bit
```python
# Toggle bit 6
B = X ^ 0x40    # 0x40 = 0100 0000

# Toggle bit 3
B = X ^ 0x08    # 0x08 = 0000 1000
```

### Recipe: Set/clear a bit
```python
B = X | 0x40    # SET bit 6 (force to 1)
B = X & ~0x40   # CLEAR bit 6 (force to 0)
```

### Practice exercises
1. Extract bits 4-7 from byte X
2. Combine the high nibble of X1 with the low nibble of X2 into one byte
3. Toggle bits 0 and 7 simultaneously
4. Check if bit 3 is set: write an if-statement

---

## 2. Communication Buses — Pin Locations on RPi

### GPIO header pin map (memorize these)
| Bus | Signal | GPIO (BCM) | Physical Pin |
|-----|--------|-----------|--------------|
| **I2C** | SDA | GPIO 2 | Pin 3 |
| **I2C** | SCL | GPIO 3 | Pin 5 |
| **SPI0** | MOSI | GPIO 10 | Pin 19 |
| **SPI0** | MISO | GPIO 9 | Pin 21 |
| **SPI0** | SCLK | GPIO 11 | Pin 23 |
| **SPI0** | CE0 | GPIO 8 | Pin 24 |
| **SPI0** | CE1 | GPIO 7 | Pin 26 |
| **UART** | TX | GPIO 14 | Pin 8 |
| **UART** | RX | GPIO 15 | Pin 10 |
| **3.3V** | — | — | Pin 1, 17 |
| **5V** | — | — | Pin 2, 4 |
| **GND** | — | — | Pin 6, 9, 14, 20, 25, 30, 34, 39 |

### Bus comparison (know when to use which)
| Property | SPI | I2C | UART |
|----------|-----|-----|------|
| Wires | 4 | 2 | 2 |
| Speed | Fast | Medium | Slow |
| Multiple devices | Via CS pin per device | Via address (0x27 etc.) | Point-to-point only |
| Full duplex | Yes | No | Yes |
| Clock | Master provides | Master provides | No clock (async) |
| Used for | RFID, displays, ADC | LCD, sensors, ADC | GPS, serial terminal |

### SPI specifics
- **SCLK** — clock from master
- **MOSI** — master sends data to slave
- **MISO** — slave sends data back
- **CS/CE** — pulled LOW to select a slave (active low)
- RPi has SPI0 on header; CE1 conflicts with joystick button (GPIO7) → remap to GPIO18

### I2C specifics
- Only 2 wires: SDA (data) + SCL (clock)
- Each device has a unique 7-bit address (e.g. `0x27` for LCD, `0x68` for MPU6050)
- Find addresses with: `i2cdetect -y 1`

---

## 3. ADC — Analog to Digital Conversion

- **Sampling frequency** — how many times per second you read the signal
- **Bit depth** — how many levels you can represent (8-bit = 256 levels, 12-bit = 4096)
- **Nyquist theorem** — sample at least 2× the highest frequency in your signal
- **Aliasing** — what happens when you sample too slowly (signal looks wrong)
- **Resolution** = Vref / 2^bits (e.g. 3.3V / 4096 for 12-bit)

### ADC chips used in lab
| Chip | Interface | Bits | Notes |
|------|-----------|------|-------|
| ADS1115 | I2C | 16-bit | address 0x48 |
| PCF8591 | I2C | 8-bit | address 0x48 |
| ADS7830 | I2C | 8-bit | |

---

## 4. Serial Communication

### Synchronous vs Asynchronous
- **Synchronous** (SPI, I2C) — shared clock line keeps both sides in sync
- **Asynchronous** (UART) — no clock; both sides agree on baud rate beforehand

### UART settings (both sides must match)
- Baud rate (e.g. 9600, 115200)
- Data bits (usually 8)
- Stop bits (usually 1)
- Parity (usually None)

---

## 5. Signal Theory

### dB (decibels)
```
dB = 10 * log10(P2/P1)      # power ratio
dB = 20 * log10(V2/V1)      # voltage ratio
```
- +3 dB ≈ double the power
- -3 dB ≈ half the power
- +10 dB = 10× power
- +20 dB = 100× power (or 10× voltage)

### Shannon & Nyquist
- **Nyquist capacity** (no noise): `C = 2B * log2(M)` — B = bandwidth, M = signal levels
- **Shannon capacity** (with noise): `C = B * log2(1 + S/N)` — S/N = signal-to-noise ratio

### SNR
```
SNR (dB) = 10 * log10(Signal power / Noise power)
```

---

## 6. Camera & Computer Vision

### Lens basics
- **Focal length** — shorter = wider angle, longer = more zoom
- **Aperture (f-stop)** — smaller f-number = more light = shallower depth of field
- **Resolution** — pixels on the sensor

### Color spaces
| Space | Channels | Use |
|-------|----------|-----|
| RGB | Red, Green, Blue | Display |
| BGR | Blue, Green, Red | OpenCV default |
| HSV | Hue, Saturation, Value | Color filtering/detection |
| Grayscale | 1 channel | Edge detection, faster processing |

### OpenCV basics
```python
import cv2
cap = cv2.VideoCapture(0)        # open webcam
ret, frame = cap.read()          # grab frame (BGR)
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
hsv  = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv, lower, upper)   # color filter
```

### Camera calibration
- Shoot checkerboard from 15+ angles
- `cv2.findChessboardCorners()` detects inner corners
- `cv2.calibrateCamera()` outputs camera matrix + distortion coefficients
- `cv2.undistort()` corrects future frames

### USB vs CSI (Pi 5)
| | USB Webcam | CSI Camera |
|-|-----------|-----------|
| Driver | V4L2 (`/dev/videoX`) | libcamera / Picamera2 |
| OpenCV | `cv2.VideoCapture(0)` | Use Picamera2 library |
| Speed | CPU-heavy | Hardware ISP |

---

## 7. Data Logging & Edge Computing

- **IoT logging** — store sensor readings to CSV, SQLite, or cloud
- **Edge computing** — process data close to the sensor (on Pi) instead of sending raw data to cloud → lower latency, less bandwidth
- **Gradio** — Python web UI to expose sensor data / camera feed on the network:
```python
import gradio as gr
demo = gr.Interface(fn=my_function, inputs=..., outputs=...)
demo.launch(server_name="0.0.0.0")
```

---

## 8. Lab Practical — What you need to be able to do

### Wiring
- Connect RFID (RC522) via SPI
- Connect LCD via I2C
- Connect buzzer to GPIO, control with PWM
- Connect ADC via I2C, read analog values
- Connect LED matrix via shift register

### Code skills
- Write modular Python (classes, functions, separate files)
- Use `RPi.GPIO` or `gpiozero` for GPIO
- Read I2C devices with `smbus2`
- Use `mfrc522` for RFID
- Use `cv2` for camera
- Use `subprocess` to call `ffmpeg`
- Use `threading` for parallel tasks

### GPIO safety rules
- Never connect 5V to a GPIO input (max 3.3V)
- Always use `GPIO.cleanup()` at the end
- RC522 is 3.3V only — do NOT use 5V

---

## 9. Quick reference — Hex/Binary

| Hex | Binary | Decimal |
|-----|--------|---------|
| 0x0F | 0000 1111 | 15 |
| 0xF0 | 1111 0000 | 240 |
| 0xFF | 1111 1111 | 255 |
| 0x40 | 0100 0000 | 64 |
| 0x80 | 1000 0000 | 128 |
| 0x01 | 0000 0001 | 1 |

---

## 10. Exam day checklist

- [ ] USB with all your lab code from week01–week11
- [ ] Know how to copy code from USB and run it
- [ ] Know pin numbers for I2C, SPI, UART from memory
- [ ] Can solve bit extraction/toggle problems step by step
- [ ] Can explain SPI vs I2C vs UART differences
- [ ] Know Nyquist theorem and Shannon formula
- [ ] Know dB formulas (power and voltage)
- [ ] Can explain what ADC bit depth and sampling frequency mean
