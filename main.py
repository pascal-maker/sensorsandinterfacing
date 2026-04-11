"""
main.py — Multi-mode sensor station
====================================
Combines all week classes into one interactive demo.

Hardware used
-------------
  GPIO 20        → MODE button  (cycles modes 0 → 1 → 2)
  GPIO 26        → ACTION button (context-sensitive per mode)
  GPIO 16,21     → BCD buttons b2, b3  (mode 2)
  GPIO  5, 6, 13 → RGB LED (R, G, B)
  GPIO 17        → single LED
  GPIO 18        → servo signal
  GPIO 14, 15    → DC motor (H-bridge)
  GPIO 19,13,6,5 → stepper coils   ← NOTE: GPIO 13 & 6 shared with RGB
                                      swap stepper pins if using both
  I2C            → MPU6050 @ 0x68
  I2C            → ADS7830 @ 0x48

Modes
-----
  0 — IMU mode  (Blue RGB)
        MPU6050 accel-X  →  servo angle
        prints accel / gyro / temp every 0.5 s

  1 — Motor mode  (Green RGB)
        ADS7830 ch2 potentiometer → DC motor speed
        ACTION button toggles direction (forward / reverse / stop)

  2 — BCD mode  (Red RGB)
        4 buttons read as 4-bit BCD value
        LED blinks that many times on ACTION press
"""

import RPi.GPIO as GPIO
import time
import threading

# ── import all week classes ────────────────────────────────────────────────
from week1.gpio_basics    import LED, Button
from week4.pwm_adc        import ADS7830, RGBLed
from week5.communication  import ServoMotor
from week6.mpu6050        import MPU6050
from week07.motors        import DCMotor
from week3.bit_operations import BCDReader

# ── pin assignments ────────────────────────────────────────────────────────
PIN_MODE_BTN   = 20
PIN_ACTION_BTN = 26
PIN_LED        = 17
PIN_SERVO      = 18
PIN_DC1        = 14
PIN_DC2        = 15
BCD_PINS       = [16, 21, 19, 13]   # b0..b3  (avoid RGB & stepper overlap)

# ── setup ──────────────────────────────────────────────────────────────────
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

mode_btn   = Button(PIN_MODE_BTN)
action_btn = Button(PIN_ACTION_BTN)
led        = LED(PIN_LED)
rgb        = RGBLed(pin_r=5, pin_g=6, pin_b=13)
servo      = ServoMotor(PIN_SERVO)
dc         = DCMotor(PIN_DC1, PIN_DC2)
imu        = MPU6050()
adc        = ADS7830()
bcd        = BCDReader(BCD_PINS)

imu.set_accel_range(0)   # ±2 g
imu.set_gyro_range(0)    # ±250 °/s

# ── state ──────────────────────────────────────────────────────────────────
MODE_NAMES  = ["IMU", "MOTOR", "BCD"]
MODE_COLORS = [
    (0,   0,   255),   # blue  — IMU
    (0,   255, 0  ),   # green — MOTOR
    (255, 0,   0  ),   # red   — BCD
]

current_mode  = 0
dc_direction  = 0   # 0=stop, 1=forward, 2=reverse
_lock         = threading.Lock()


def set_mode(new_mode):
    global current_mode, dc_direction
    with _lock:
        current_mode = new_mode % len(MODE_NAMES)
        dc_direction = 0
        dc.stop()
        servo._pwm.ChangeDutyCycle(0)
        r, g, b = MODE_COLORS[current_mode]
        rgb.set_color(r, g, b)
        print(f"\n=== Mode {current_mode}: {MODE_NAMES[current_mode]} ===")


def blink_led(times):
    """Blink the single LED `times` times (blocking, run in thread)."""
    for _ in range(times):
        led.on()
        time.sleep(0.2)
        led.off()
        time.sleep(0.2)


# ── mode 0: IMU ─────────────────────────────────────────────────────────────
def run_imu_mode():
    data = imu.read()
    ax, ay, az = data["accel_g"]
    gx, gy, gz = data["gyro_dps"]

    # Map accel-X  (-1g … +1g)  →  servo angle (0 … 180°)
    angle = max(0, min(180, int((ax + 1.0) / 2.0 * 180)))
    servo.set_angle(angle, hold_ms=200)

    print(
        f"[IMU] accel=({ax:+.2f}, {ay:+.2f}, {az:+.2f})g  "
        f"gyro=({gx:+.1f}, {gy:+.1f}, {gz:+.1f})°/s  "
        f"temp={data['temp_c']:.1f}°C  → servo {angle}°"
    )
    time.sleep(0.5)


# ── mode 1: MOTOR ───────────────────────────────────────────────────────────
def run_motor_mode():
    global dc_direction

    # ACTION button cycles direction: stop → forward → reverse → stop
    if action_btn.fell():
        dc_direction = (dc_direction + 1) % 3
        labels = ["STOP", "FORWARD", "REVERSE"]
        print(f"[MOTOR] direction → {labels[dc_direction]}")

    speed_raw = adc.read_raw(2)                      # potentiometer on ch2
    speed_pct = int(speed_raw * 100 / 255)

    if dc_direction == 0:
        dc.stop()
    elif dc_direction == 1:
        dc.forward(speed_pct)
    else:
        dc.reverse(speed_pct)

    print(f"[MOTOR] ADC={speed_raw:3d} → {speed_pct:3d}%  dir={dc_direction}")
    time.sleep(0.1)


# ── mode 2: BCD ─────────────────────────────────────────────────────────────
def run_bcd_mode():
    value = bcd.read_value()
    bits  = bcd.read_bits()
    print(f"[BCD] bits={bits}  value={value}")

    # ACTION button triggers LED blink burst
    if action_btn.fell():
        if value > 0:
            print(f"[BCD] blinking LED {value} times")
            threading.Thread(target=blink_led, args=(value,), daemon=True).start()
        else:
            print("[BCD] value is 0, nothing to blink")

    time.sleep(0.2)


# ── main loop ──────────────────────────────────────────────────────────────
def main():
    set_mode(0)
    print("Press MODE button (GPIO 20) to cycle modes.")
    print("Press CTRL+C to exit.\n")

    try:
        while True:
            # Mode button: cycle on falling edge
            if mode_btn.fell():
                set_mode(current_mode + 1)

            with _lock:
                mode = current_mode

            if mode == 0:
                run_imu_mode()
            elif mode == 1:
                run_motor_mode()
            elif mode == 2:
                run_bcd_mode()

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        dc.cleanup()
        servo.stop()
        rgb.stop()
        led.off()
        adc.close()
        imu.close()
        GPIO.cleanup()
        print("Cleanup done.")


if __name__ == "__main__":
    main()
