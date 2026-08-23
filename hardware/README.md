# Shared hardware drivers

This package contains the drivers that are genuinely reused across the course:
`ADS7830`, `Button`, `LCD`, `ServoMotor`, and `ShiftRegister`.

Completed applications may import these classes instead of copying low-level
GPIO and I2C code. Early weekly exercises intentionally keep standalone
implementations when writing that low-level code is part of the lesson.

```python
import RPi.GPIO as GPIO

from hardware import ADS7830, LCD, ServoMotor

GPIO.setmode(GPIO.BCM)
adc = ADS7830()
lcd = LCD()
servo = ServoMotor(pin=18)
```

The application that creates the devices owns cleanup. Close each object before
calling `GPIO.cleanup()`.
