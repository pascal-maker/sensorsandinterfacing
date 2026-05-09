### Assignment-specific explanation

Screen 5 reads accelerometer data from the **MPU** and shows:

```text
Line 1: X left    Y right
Line 2: Z left    Combined right
```

The important parts are:

```python
MPU_ADDR = 0x68
PWR_MGMT_1 = 0x6B
```

The MPU is at I2C address `0x68`.
`PWR_MGMT_1` is used to wake the sensor up.

```python
def mpu_init():
    bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0)
```

This wakes up the MPU. Without this, the sensor may stay in sleep mode.

```python
raw_x = read_word_2c(ACCEL_XOUT_H)
raw_y = read_word_2c(ACCEL_YOUT_H)
raw_z = read_word_2c(ACCEL_ZOUT_H)
```

This reads the raw 16-bit accelerometer values for X, Y and Z.

Important correction in your code:

```python
if val >= 0x8000:
    val = val - 65536
```

You currently have this twice. Remove the second one:

```python
if val >= 0x8000:
    val = val - 65536
```

Only subtract `65536` once.

```python
x_g = raw_x / ACCEL_SCALE
y_g = raw_y / ACCEL_SCALE
z_g = raw_z / ACCEL_SCALE
```

This converts raw accelerometer values to **g-force**.

```python
combined_g = math.sqrt(x_g**2 + y_g**2 + z_g**2)
```

This calculates the total acceleration using the vector magnitude.

```python
line1 = left1.ljust(8) + right1.rjust(8)
line2 = left2.ljust(8) + right2.rjust(8)
```

This aligns X and Z left, and Y and combined right.

### Oral explanation

> “This script reads accelerometer data from the MPU over I2C. First I wake the MPU by writing 0 to the power management register. Then I read the X, Y and Z accelerometer registers as signed 16-bit values. I convert the raw values to g by dividing by 16384. Then I calculate the combined acceleration with the square root of X squared plus Y squared plus Z squared. Finally I display X and Y on the first LCD line, and Z and combined g on the second line, formatted to two decimals.”

## 5 oral questions + answers

### 1. Why do you call `mpu_init()`?

To wake up the MPU. The sensor can start in sleep mode, so I write `0` to the power management register `0x6B`.

### 2. Why do you read two bytes for each axis?

Each accelerometer value is a 16-bit value. I read the high byte and low byte, then combine them into one number.

### 3. What does this line do?

```python
val = (high << 8) | low
```

It shifts the high byte 8 bits to the left and combines it with the low byte. This creates one 16-bit value.

### 4. Why do you subtract `65536`?

Because the MPU gives signed values using two’s complement. If the value is above `0x8000`, it represents a negative number, so subtracting `65536` converts it to the correct negative value.

### 5. How do you calculate the combined acceleration?

With the vector magnitude formula:

```python
combined_g = sqrt(x² + y² + z²)
```

So the combined value includes acceleration from all three axes.

---

## Exam practice questions

### Q1. Why does `mpu_init()` write `0` to register `0x6B`, and what happens if you skip it?

The MPU6050 starts in sleep mode by default every time it powers on. Writing `0` to the `PWR_MGMT_1` register (`0x6B`) wakes it up. If you skip this the sensor stays asleep and returns no data — the LCD would show zeros for every axis.

---

### Q2. Why does reading one axis value require two bytes?

Each axis value is 16 bits of data. The I2C bus can only send 8 bits at a time, so the sensor stores the result across two registers — one for the high byte and one for the low byte. You must read both and combine them yourself.

---

### Q3. What does `val = (high << 8) | low` do, and what would break if you just returned `high`?

`high << 8` shifts the high byte 8 positions left to make room for the low byte. `| low` slots the low byte into those 8 empty positions, producing one 16-bit number. If you returned `high` alone you would only have 8 bits of data and lose all the precision stored in the low byte.

---

### Q4. Why is `val - 65536` used when `val >= 0x8000`?

This handles two's complement. In a 16-bit signed number, if the first (most significant) bit is `1`, the number is negative. `0x8000` is where that bit switches on. Subtracting 65536 (= 2¹⁶, the total range of a 16-bit number) converts the raw unsigned value into the correct negative number.

Example: raw value `65500 - 65536 = -36`

---

### Q5. Where does `16384` come from, and what does a result of `1.0` mean?

The MPU6050 in its default ±2g range is calibrated so that `16384 raw units = 1g`. This comes from the chip's datasheet. Dividing the raw value by `16384` converts it to g-force. A result of `1.0` means 1g — the normal pull of Earth's gravity. If the sensor is lying flat and still, the Z axis should read approximately `1.0`.
