import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
servopin = 18
GPIO.setup(servopin, GPIO.OUT)

def angle_to_duty_cycle(angle):#function accepts angle 
    # 0° = 2.5% (0.5ms pulse), 180° = 12.5% (2.5ms pulse) at 50Hz
    return (angle / 180) * 10 + 2.5#returns duty cycle 

servo_pwm = GPIO.PWM(servopin, 50)#sets the frequency to 50Hz
servo_pwm.start(angle_to_duty_cycle(0))# starts servo at 0 degrees

servo_pwm.ChangeDutyCycle(angle_to_duty_cycle(180))#changes duty cycle to 180 degrees
time.sleep(3)
servo_pwm.ChangeDutyCycle(angle_to_duty_cycle(90))#changes duty cycle to 90 degrees
time.sleep(3)

servo_pwm.stop()
GPIO.cleanup()
"""
A servo at 50Hz expects pulses between 0.5ms and 2.5ms to set its position:                                   
   
  0°   → 0.5ms pulse → 2.5% duty cycle                                                                          
  90°  → 1.5ms pulse → 7.5% duty cycle                      
  180° → 2.5ms pulse → 12.5% duty cycle
                                                                                                                
  The formula (angle / 180) * 10 + 2.5 just does that math:
  - Divide by 180 to get a 0–1 fraction of the full range                                                       
  - Multiply by 10 (the range is 12.5 - 2.5 = 10)                                                               
  - Add 2.5 (the minimum)                        
                                                                                                                
  So angle_to_duty_cycle(90) gives (90/180) * 10 + 2.5 = 0.5 * 10 + 2.5 = 7.5."""