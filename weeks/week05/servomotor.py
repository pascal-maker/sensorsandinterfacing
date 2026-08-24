import RPi.GPIO as GPIO#
import time

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

SERVO_PIN = 18          # GPIO pin connected to servo signal
PWM_FREQUENCY = 50      # Servo uses 50 Hz -> period = 20 ms

# Practical pulse width range for full movement
# Often works better than only 1.0 ms to 2.0 ms
MIN_PULSE_MS = 0.6      # around 0 degrees
MAX_PULSE_MS = 2.4      # around 180 degrees


# --------------------------------------------------
# SETUP
# --------------------------------------------------

GPIO.setmode(GPIO.BCM)#set the mode to BCM
GPIO.setup(SERVO_PIN, GPIO.OUT)#set the servo pin as output

servo_pwm = GPIO.PWM(SERVO_PIN, PWM_FREQUENCY)#create a PWM instance
servo_pwm.start(0)   # start with 0% duty cycle


# --------------------------------------------------
# HELPER FUNCTION
# --------------------------------------------------

def angle_to_duty_cycle(angle):#convert angle to duty cycle
    """
    Convert an angle (0 to 180 degrees)
    to the matching duty cycle for the servo.

    Step 1:
    Map angle 0..180 to pulse width 0.6..2.4 ms

    Step 2:
    Convert pulse width to duty cycle percentage
    using a 20 ms period (50 Hz)
    """

    # Keep angle inside valid range
    if angle < 0:#if the angle is less than 0, set it to 0
        angle = 0
    elif angle > 180:#if the angle is greater than 180, set it to 180
        angle = 180

    # Map angle to pulse width
    pulse_width_ms = MIN_PULSE_MS + (angle / 180.0) * (MAX_PULSE_MS - MIN_PULSE_MS)#convert angle to pulse width

    # Convert pulse width to duty cycle percentage
    duty_cycle = (pulse_width_ms / 20.0) * 100.0#convert pulse width to duty cycle percentage

    return duty_cycle#return the duty cycle


def set_angle(angle):#move servo to the given angle
    """
    Move servo to the given angle.
    """
    duty = angle_to_duty_cycle(angle)#convert angle to duty cycle
    print(f"Angle: {angle}° -> Duty cycle: {duty:.2f}%")#print the angle and duty cycle

    servo_pwm.ChangeDutyCycle(duty)

    # Give servo time to move
    time.sleep(0.5)

    # Optional: stop sending strong holding signal after move
    # This can reduce jitter on some servos
    servo_pwm.ChangeDutyCycle(0)


# --------------------------------------------------
# TEST PROGRAM
# --------------------------------------------------

try:
    # Test some fixed angles
    set_angle(0)#set the angle to 0
    time.sleep(1)#wait for 1 second

    set_angle(90)#set the angle to 90
    time.sleep(1)#wait for 1 second

    set_angle(180)#set the angle to 180
    time.sleep(1)#wait for 1 second

    # Sweep through angles
    for angle in range(0, 181, 30):#sweep through angles from 0 to 180 in steps of 30
        set_angle(angle)#set the angle to the current angle
        time.sleep(0.8)#wait for 0.8 seconds

    for angle in range(180, -1, -30):#sweep through angles from 180 to 0 in steps of -30
        set_angle(angle)#set the angle to the current angle
        time.sleep(0.8)#wait for 0.8 seconds

except KeyboardInterrupt:
    print("Program stopped by user.")

finally:
    servo_pwm.stop()#stop the PWM
    del servo_pwm#delete the PWM instance
    GPIO.cleanup()#cleanup the GPIO pins
    print("Cleanup done.")