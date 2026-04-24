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
