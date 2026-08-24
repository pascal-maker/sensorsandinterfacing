# Week 08 Assignment — Full Explanation

---

## 1. What is the goal of this code?

The program reads a **potentiometer** (a rotating knob) using an ADC chip over I2C.
The knob value (0–255) controls two things at the same time:

- **LED bar graph** — shows how far the knob is turned (1–10 LEDs light up)
- **Buzzer** — the pitch gets higher as you turn the knob further

A **button** switches between two LED display modes:
- **Single mode** — only ONE LED lights up at the current position
- **Fill mode** — ALL LEDs up to the current position light up

---

## 2. What hardware/components are involved?

| Component | What it does |
|-----------|-------------|
| **Potentiometer** | Rotating knob — gives analog value 0–255 |
| **PCF8591** | ADC chip — converts analog voltage into digital number (I2C) |
| **74HC595 Shift Register** | Receives bits one at a time and controls 8+ outputs (LEDs) |
| **LED Bar Graph** | 10 LEDs in a row — shows the knob position visually |
| **Buzzer** | Makes sound — pitch changes with the knob |
| **Push Button** | Toggles between single LED and fill LED mode |
| **Raspberry Pi** | Runs the code and controls everything |

---

## 3. What are the important GPIO pins / protocols?

| Pin / Protocol | Used for | Why |
|----------------|----------|-----|
| GPIO 20 | Button input | Read button press |
| GPIO 12 | Buzzer output (PWM) | Send PWM signal to buzzer |
| GPIO 22 | Shift register DATA | Send bits one at a time |
| GPIO 17 | Shift register CLOCK | Tell register to read the bit |
| GPIO 27 | Shift register LATCH | Copy bits to outputs (show LEDs) |
| **I2C (bus 1)** | Talk to PCF8591 ADC | Read analog potentiometer value |
| **PWM** | Buzzer frequency + duty cycle | Control pitch and volume |

---

## 4. Important lines — what breaks if you remove them?

---

### `GPIO.setmode(GPIO.BCM)`
Uses **BCM pin numbering** (the GPIO numbers printed on the Pi).
Without this: pin numbers mean nothing — wrong pins fire.

---

### `GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)`
Sets the button as **input with pull-up resistor**.
The pull-up keeps the pin at HIGH when the button is NOT pressed.
Without it: the pin floats between HIGH and LOW randomly — false triggers.

---

### `bouncetime=300`
Prevents **button bounce** — when you press a physical button it rapidly bounces between HIGH and LOW for a few milliseconds.
Without it: one press registers as 5–10 presses.

---

### `bus.read_byte(I2C_ADDRESS)` (first/dummy read)
The PCF8591 returns the result of the **previous conversion**, not the current one.
The dummy read **throws away the old stale value**.
The second read gives the **fresh correct value**.
Without it: you always read one step behind — wrong values.

---

### `bus.write_byte(I2C_ADDRESS, 0x40 | (channel & 0x03))`
Tells the PCF8591 **which channel to read** (A0–A3).
`0x40` is the control byte. `& 0x03` limits channel to 0–3 safely.
Without it: reads the wrong channel or no channel at all.

---

### `global fill_mode`
Makes `fill_mode` refer to the **global variable**, not a local copy.
Without it: the toggle only changes a local copy inside the function — the real `fill_mode` never changes.

---

### `copy_to_storage_register()` / latch pulse
The shift register holds bits internally but does NOT show them on output pins until the **latch goes HIGH then LOW**.
Without it: LEDs never update — they stay off or stuck.

---

### `GPIO.PWM(BUZZER, 100)` + `buzzer_pwm.start(50)`
Creates a **PWM signal** on the buzzer pin.
PWM lets us control **frequency (pitch)** and **duty cycle (volume)**.
A simple GPIO HIGH/LOW would only make one fixed tone.
Without PWM: no control over pitch or volume.

---

### `buzzer_pwm.stop()` + `GPIO.cleanup()` in `finally`
The `finally` block **always runs** — even after CTRL+C.
Without it: buzzer keeps buzzing after program ends, LEDs stay on, GPIO pins stay configured.

---

## 5. How could the teacher modify this on the exam?

| Modification | What you need to know |
|---|---|
| Change channel from A2 to A0 | Change `read_channel(2)` to `read_channel(0)` |
| Remove the dummy read | Explain why values are one step behind |
| Remove `bouncetime` | Explain button bounce problem |
| Remove `pull_up_down=GPIO.PUD_UP` | Explain floating pin problem |
| Remove `global fill_mode` | Explain local vs global scope |
| Remove latch pulse | Explain why LEDs never update |
| Change `GPIO.FALLING` to `GPIO.RISING` | Trigger on release instead of press |
| Change duty cycle from 50 to 10 | Explain effect on buzzer volume |
| Change fill=True/False | Explain difference between fill and single LED mode |
| Ask you to draw the bit pattern for value=3 or value=7 | See bit pattern section below |

---

## 6. Bit Pattern Examples

### Fill mode: `pattern = (1 << value) - 1`

**How it works — like magic subtraction:**

```
value = 4

Step 1: shift 1 left by 4
  00000001
  << 4
= 00010000

Step 2: subtract 1
  00010000
-        1
----------
  00001111
```

The computer borrows from all the zeros — they all flip to 1.
Result: 4 LEDs ON (positions 1–4).

---

**With value = 6:**

```
Step 1: 1 << 6 = 01000000
Step 2: 01000000 - 1
      = 00111111
```

LEDs 1, 2, 3, 4, 5, 6 ON. Filled effect.

---

### Single LED mode: `pattern = 1 << (value - 1)`

```
value = 4

1 << (4-1) = 1 << 3 = 00001000
```

Only LED 4 ON.

```
value = 6

1 << (6-1) = 1 << 5 = 00100000
```

Only LED 6 ON.

---

## 7. PCF8591 — I2C ADC Chip

```python
I2C_ADDRESS = 0x48
bus = smbus2.SMBus(1)
```

- The PCF8591 reads **analog voltages** (like the potentiometer) and converts them to a **digital number 0–255**
- It communicates over **I2C** — a 2-wire protocol (SDA data + SCL clock)
- Address `0x48` identifies this specific chip on the I2C bus
- `SMBus(1)` opens I2C bus number 1 on the Raspberry Pi
- Without this chip: the Raspberry Pi cannot read analog signals at all — it only has digital GPIO pins

---

## 8. Shift Register — 3-Pin Serial Communication

The shift register (74HC595) needs only 3 GPIO pins to control 8+ LEDs:

| Pin | Role |
|-----|------|
| DATA | The bit (0 or 1) to send |
| CLOCK | Pulse to shift the bit in |
| LATCH | Pulse to copy bits to output |

**Why MSB first (bit 7 down to bit 0)?**
Because the first bit shifted in ends up at the far end of the register.
Sending from bit 7 first means bit 7 lands at output Q7, bit 0 lands at Q0 — correct order.

---

## 9. Frequency Scaling

```python
frequency = 100 + int((analog_value / 255) * 1000)
```

- Potentiometer at minimum (0): frequency = 100 + 0 = **100 Hz** (low pitch)
- Potentiometer at maximum (255): frequency = 100 + 1000 = **1100 Hz** (high pitch)
- The knob controls both the LEDs AND the pitch at the same time

---

## 10. LED Scaling

```python
led_value = int((analog_value / 255) * 10)
if led_value == 0:
    led_value = 1
```

- Maps 0–255 into 0–10 LEDs
- Forces minimum 1 LED so the bar graph is never completely empty
- Without scaling: you would send raw values 0–255 directly but the bar only has 10 LEDs

● Two different patterns, two different effects
                                           
  ---
  Pattern 1 — Fill mode (all LEDs up to position)                                                                      
                                                                                                                       
  pattern = (1 << value) - 1                                                                                           
                                                                                                                       
  Think of it in 2 steps:                                                                                              
   
  Step 1 — shift 1 left by value places:                                                                               
  value = 4            
           
  00000001  << 4  =  00010000                                                                                          
                             
  Step 2 — subtract 1:                                                                                                 
    00010000                                                                                                           
  -        1
  ----------                                                                                                           
    00001111           
            
  Why does subtracting 1 fill everything below? Because there are no 1-bits to borrow from — the computer is forced to
  borrow all the way down, flipping every zero to a one.                                                               
          # 00001000                                                                                                   
          else:                                                                                                        
              pattern = 1 << (value - 1) first exlainme this                                                           

● Two different patterns, two different effects

  ---
  Pattern 1 — Fill mode (all LEDs up to position)

  pattern = (1 << value) - 1

  Think of it in 2 steps:

  Step 1 — shift 1 left by value places:
  value = 4

  00000001  << 4  =  00010000

  Step 2 — subtract 1:
    00010000
  -        1
  ----------
    00001111

  Why does subtracting 1 fill everything below? Because there are no 1-bits to borrow from — the computer is forced to
  borrow all the way down, flipping every zero to a one.

  Result: LEDs 1, 2, 3, 4 all ON

  ---
  Pattern 2 — Single LED mode (only ONE LED at position)

  pattern = 1 << (value - 1)

  Only one shift, no subtraction:
  value = 4

  1 << (4-1)  =  1 << 3  =  00001000

  Result: Only LED 4 ON

  ---
  Side by side for value = 4

  Fill mode:    00001111   (LEDs 1,2,3,4 ON)
  Single mode:  00001000   (only LED 4 ON)

  ---
  Pattern 2 — Single LED mode (only ONE LED at position)

  pattern = 1 << (value - 1)

  Only one shift, no subtraction:
  value = 4

  1 << (4-1)  =  1 << 3  =  00001000

  Result: Only LED 4 ON

  ---
  Side by side for value = 4

  Fill mode:    00001111   (LEDs 1,2,3,4 ON)
  Single mode:  00001000   (only LED 4 ON)

  ---
  Why value - 1 in single mode but not fill mode?

  - Fill mode shifts past the target position and subtracts — the -1 is the subtraction itself
  - Single mode shifts directly to the target, but bit positions start at 0, so LED 4 is at bit position 3 — you
  subtract 1 to correct for that

  Fill mode:    00001111   (LEDs 1,2,3,4 ON)
  Single mode:  00001000   (only LED 4 ON)

  ---
  Why value - 1 in single mode but not fill mode?

  - Fill mode shifts past the target position and subtracts — the -1 is the subtraction itself
  - Single mode shifts directly to the target, but bit positions start at 0, so LED 4 is at bit position 3 — you
   subtract 1 to correct for that

✻ Cooked for 9s

❯   1. The button uses GPIO.FALLING — what does that mean physically? When your finger presses down, does the   
  pin go HIGH                                                                                                   
     or LOW?    the anwer to that questio n is the pin goes low because interall pull up 2) the shift rgesoter  
  needs a latch lin beacuse  to copy puls bit to an ouput without a latch pin the bits woudl heeld internallya  
  dn woulnt show up in the leds so egt lost  3) the led bar graphy would be empty 4) the buzzer would go offt   
  the whole time 5) duty cycle actually tells you how long it stays in a cetrain frqeueny it says for 50        
  percent of time cycle it satys in this frequency if you lower it to 10 perent its ays dor duration fothe      
  cycle it stays 10 onthis freuency                                                                             
                                                                                                                
● Your answers — feedback on each                                                                               
                                         
  ---                                                                                                           
  1. GPIO.FALLING — pin goes LOW because of pull-up
  CORRECT. Pull-up holds pin HIGH normally. Press button → connects to ground → pin goes LOW. FALLING = HIGH to 
  LOW transition.                                           
                                                                                                                
  ---                                                       
  2. Latch pin needed to copy bits to output                                                                    
  CORRECT. Small correction: the bits are not lost — they are sitting safely inside the shift register's        
  internal memory. They just stay hidden there until the latch pulse copies them to the output pins where the
  LEDs can see them.                                                                                            
                                                            
  ---                                                                                                           
  3. LED bar would be empty when potentiometer all the way down
  CORRECT.                                                                                                      
  
  ---                                                                                                           
  4. Dummy read — your answer is wrong here                 
  You said "buzzer goes off the whole time" — that is the answer to a different question.                       
                                                                                         
  The correct answer is:                                                                                        
                                                                                                                
  ▎ You would read the old stale value from the previous conversion. So the program is always one step behind   
  ▎ what the potentiometer actually is. Turn the knob to position 5, but the program still acts on position 4.  
                                                                                                                
  ---                                                       
  5. Duty cycle — this is wrong, be careful
                                                                                                                
  Duty cycle has nothing to do with frequency. You are mixing the two up.
                                                                                                                
  - Frequency = how many times per second the signal repeats = controls pitch                                   
  - Duty cycle = how long the signal stays HIGH inside one cycle = controls volume/loudness                     
                                                                                                                
  50% duty cycle:   HIGH --- LOW ---   (half on, half off)  → normal volume
  10% duty cycle:   HIGH - LOW -------  (barely on)         → much quieter                                      
                                                                                                                
  Changing duty cycle makes the buzzer louder or quieter, not higher or lower pitch.                            
                                                                            