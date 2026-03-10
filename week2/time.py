import RPi.GPIO as GPIO
import time
import csv

BTN = 20
LED = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BTN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED, GPIO.OUT)

filename = time.strftime("button_data_%Y%m%d_%H%M%S.csv")

timestamps = []
press_states = []

try:
    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        btn_state = GPIO.input(BTN)

        if btn_state == 0:
            current_state = "Pressed"
            GPIO.output(LED, GPIO.HIGH)
        else:
            current_state = "Released"
            GPIO.output(LED, GPIO.LOW)

        timestamps.append(timestamp)
        press_states.append(current_state)

        print(f"{timestamp} - Button is {current_state}")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("Program stopped by user")

finally:
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Timestamp", "Button State"])
        for ts, state in zip(timestamps, press_states):
            writer.writerow([ts, state])

    GPIO.cleanup()
    
 #This script stores when the button is released or pressed and writes that into a CSV file. It also saves the timestamp for each reading. Because the button uses GPIO.PUD_UP, the normal state is released = 1, and when you press it, it becomes 0. If the button is pressed, the script saves "Pressed" and turns the LED on. If it is released, it saves "Released" and turns the LED off. All of this is written to the CSV file together with the time.   