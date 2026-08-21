# Communications & Electronics Exam — Q&A Study Guide

---

# 1. Frequency and Period

## Q: A periodic signal with a period time of 4s has a frequency of?

### Formula

[
f = \frac{1}{T}
]

Where:

* (f) = frequency in Hz
* (T) = period in seconds

### Calculation

[
f = \frac{1}{4} = 0.25Hz
]

✅ Answer: **0.25 Hz**

### Why?

Frequency means:

```text
how many waves happen per second
```

If one wave takes 4 seconds, then only 0.25 waves happen every second.

---

## Q: A periodic signal with a frequency of 2Hz has a period time of?

### Formula

[
T = \frac{1}{f}
]

### Calculation

[
T = \frac{1}{2} = 0.5s
]

✅ Answer: **0.5 seconds**

### Why?

A 2Hz signal makes:

```text
2 waves every second
```

So one wave lasts half a second.

---

# 2. Signal Parameters

## Q: What is amplitude?

✅ Answer: The vertical distance from the middle line to the peak.

### Why?

Amplitude measures the strength/height of the signal.

---

## Q: What is peak-to-peak value?

✅ Answer: The vertical distance from the highest point to the lowest point.

### Why?

It measures the TOTAL signal height.

---

## Q: What is the period?

✅ Answer: One complete horizontal cycle of the signal.

### Why?

The period tells how long one wave lasts.

---

## Q: What is a rising edge?

✅ Answer: A transition from LOW to HIGH.

---

## Q: What is a falling edge?

✅ Answer: A transition from HIGH to LOW.

---

# 3. PWM Signals

## Q: A PWM signal is high for 10ms and low for 40ms. What is the duty cycle?

### Total period

[
10ms + 40ms = 50ms
]

### Formula

[
Duty\ Cycle = \frac{T_{high}}{T_{total}} \times 100%
]

### Calculation

[
\frac{10}{50} \times 100 = 20%
]

✅ Answer: **20%**

### Why?

The signal is ON only 20% of the total time.

---

## Q: A PWM signal is high for 10ms and low for 40ms. What is the frequency?

### Total period

[
50ms = 0.05s
]

### Formula

[
f = \frac{1}{T}
]

### Calculation

[
f = \frac{1}{0.05} = 20Hz
]

✅ Answer: **20Hz**

---

# 4. Sensors, Transducers, Actuators

## Q: What is a transducer?

✅ Answer:

```text
An element that converts a physical parameter into a communication signal
```

### Examples

* microphone
* temperature sensor
* ultrasonic sensor

---

## Q: What is a sensor?

✅ Answer:

```text
Converts a physical parameter into a signal
```

### Why?

Sensors measure the physical world and generate electrical signals.

---

## Q: What is an actuator?

✅ Answer:

```text
Converts a signal into a physical change
```

### Examples

* motor
* LED
* speaker
* heater

---

# 5. Analog vs Digital Values

## Analog values

Analog means:

```text
continuous values
```

### Examples

✅ Temperature
✅ Speed
✅ Air pressure
✅ Distance
✅ Precipitation

---

## Digital values

Digital means:

```text
fixed states or counting
```

### Examples

✅ Traffic light state
✅ Visitor counter
✅ ON/OFF lamp
✅ Free disk space

---

# 6. AC and DC

## AC (Alternating Current)

✅ Signal alternates positive and negative.

### Example

* sine waves

---

## DC (Direct Current)

✅ Signal keeps same polarity.

### Example

* battery voltage

---

# 7. Sampling and ADC

## Q: Highest signal frequency is 10kHz. Minimum sample rate?

### Nyquist theorem

[
f_s \ge 2f_{max}
]

### Calculation

[
2 \times 10kHz = 20kHz
]

✅ Answer: **20kHz**

### Why?

Sampling must be at least twice the highest signal frequency.

---

## Q: Quantization noise can be reduced by?

✅ Answer:

```text
Removing the noise with a low-pass filter
```

---

## Q: ADC accuracy depends on?

✅ Answer:

```text
Both range and resolution
```

### Why?

* more bits = finer steps
* smaller range = better precision

---

## Q: ADC range -1.5V to +1.5V, 8-bit. What is the LSB?

### Range

[
3V
]

### Levels

[
2^8 = 256
]

### Formula

[
LSB = \frac{Range}{2^n}
]

### Calculation

[
\frac{3}{256} \approx 0.0117V
]

✅ Answer: **12mV**

---

## Q: ADC range 0-5V, 8-bit, value 00000101. Input voltage?

### LSB

[
\frac{5}{256} = 0.0195V
]

### Value

[
5 \times 0.0195 = 0.0976V
]

✅ Answer: **98mV**

---

# 8. RS232 Communication

## Q: RS232 1200-8E2. Bits per byte?

### Breakdown

```text
1 start
8 data
1 parity
2 stop
```

### Total

```text
12 bits
```

✅ Answer: **12 bits**

---

## Q: Time to send 1200 bytes with 1200-8E2?

### Total bits

[
1200 \times 12 = 14400bits
]

### Time

[
\frac{14400}{1200} = 12s
]

✅ Answer: **12 seconds**

---

## Q: Time to send 1MB using 9600-8N1?

### Bits per byte

```text
1 start
8 data
1 stop
= 10 bits
```

### Total bits

[
1,000,000 \times 10 = 10,000,000bits
]

### Time

[
\frac{10,000,000}{9600} \approx 1042s
]

### Minutes

[
\approx 18.2min
]

✅ Answer: **18.2 minutes**

---

# 9. Communication Types

## Simplex

✅ One direction only.

### Example

* radio broadcast

---

## Half-duplex

✅ Both directions, but one at a time.

### Example

* walkie-talkie

---

## Full-duplex

✅ Both directions simultaneously.

### Example

* telephone call

---

# 10. SPI and I²C

## MOSI

```text
Master Out Slave In
```

### On slave

✅ input

---

## MISO

```text
Master In Slave Out
```

### On slave

✅ output

---

## I²C

✅ synchronous

### Why?

Uses clock line SCL.

---

## SPI

✅ synchronous

### Why?

Uses clock line SCLK.

---

## Clock stretching

✅ I²C slave can hold clock LOW if not ready.

---

## Pull-up resistors

### SPI

❌ not required

### I²C

✅ required

### Why?

I²C uses open-drain outputs.

---

## I²C is

✅ half-duplex

---

## SPI is often

✅ full-duplex

---

## Timing source

### I²C

✅ master

### SPI

✅ master

---

## SPI connections for 5 slaves

### Needed

* MOSI
* MISO
* SCLK
* 5 chip-select lines

### Total

```text
8 connections
```

---

## I²C connections for 5 slaves

### Needed

* SDA
* SCL
* GND

### Total

```text
3 connections
```

---

## Faster interface

✅ SPI

---

## Lower power interface

✅ I²C

---

## Easier without bidirectional I/O

✅ SPI

---

## SPI masters

✅ Usually one master only.

---

## I²C masters

✅ Multiple masters possible.

---

# 11. Manchester Encoding

## Q: What is Manchester encoding used for?

✅ Ensures no long constant signal levels.

### Why?

It improves synchronization and clock recovery.

---

# 12. Modulation Techniques

## AM

```text
Amplitude Modulation
```

Amplitude changes.

---

## FM

```text
Frequency Modulation
```

Frequency changes.

### Constant power?

✅ Yes.

---

## ASK

```text
Amplitude Shift Keying
```

Digital amplitude changes.

---

## FSK

```text
Frequency Shift Keying
```

Digital frequency changes.

---

## PSK

```text
Phase Shift Keying
```

Digital phase changes.

---

## BPSK

✅ Highest noise immunity.

### Why?

Only two phase states.

---

## QAM-256

✅ Highest data rate.

### Why?

Many symbols carry many bits.

---

# 13. SSB Modulation

## SSB is a form of

✅ AM

---

## Remove upper sideband

✅ LSB

---

## Remove lower sideband

✅ USB

---

## Advantages

✅ lower bandwidth
✅ lower required power

---

# 14. Antennas and RF

## Q: Passive antenna gain = 24dB

✅ directional antenna

### Why?

Passive antennas cannot create power.
High gain means energy is focused.

---

## Free-space loss depends on

✅ frequency and distance

---

## Lower RF frequencies

✅ travel further
✅ penetrate walls better

---

## Wavelength formula

[
\lambda = \frac{c}{f}
]

---

## Q: 27MHz wavelength?

### Calculation

[
\lambda = \frac{3\times10^8}{27\times10^6}
]

[
\approx 11.11m
]

✅ Answer: **11.11 meters**

---

## Q: Dipole antenna 12.5cm

Classic dipole:

[
\lambda = 2L
]

### Calculation

[
\lambda = 25cm = 0.25m
]

[
f = \frac{3\times10^8}{0.25}
]

[
= 1200MHz
]

✅ Answer: **1200MHz**

---

# 15. CRC and Parity

## EVEN parity rule

```text
Total number of 1s must be EVEN
```

---

## Answers

```text
1001 0110 → 0
0101 0100 → 1
0001 0001 → 0
1110 1100 → 1
```

---

## CRC protects against

✅ bit errors caused by disturbances

---

## CRC does NOT protect against

❌ deliberate manipulation

---

## CRC length

Polynomial:

[
x^2 + 1
]

Highest power = 2

So CRC adds:

```text
2 bits
```

---

## Example CRC

Polynomial:

[
x^3 + x + 1
]

### Convert polynomial to binary

```text
x³ x² x¹ x⁰
 1  0  1  1
```

Result:

```text
1011
```

---

## Original data

```text
11100011
```

### Add 3 zeros

```text
11100011000
```

### CRC remainder

```text
011
```

### Final transmitted message

```text
11100011011
```

✅ Answer: **11100011011**

---

# 16. Quick Exam Cheat Sheet

## Frequency & Period

```text
f = 1/T
T = 1/f
```

---

## PWM

```text
Duty cycle = ON time / total time
```

---

## Analog

```text
continuous values
```

---

## Digital

```text
fixed states / counting
```

---

## SPI

```text
Fast
Full-duplex
More wires
No pull-ups
```

---

## I²C

```text
2 wires
Needs pull-ups
Half-duplex
Can support multiple masters
```

---

## Modulation

```text
AM  = amplitude changes
FM  = frequency changes
ASK = digital amplitude shifts
FSK = digital frequency shifts
PSK = digital phase shifts
```

---

## Noise immunity

```text
BPSK strongest
```

---

## Highest data rate

```text
QAM-256
```
