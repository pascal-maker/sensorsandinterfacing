from RPi import GPIO
import time
import csv
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

GPIO.setmode(GPIO.BCM)

btn = 20
GPIO.setup(btn, GPIO.IN, pull_up_down=GPIO.PUD_UP)
previous_state = GPIO.HIGH
press_start_time = None
rows = []

os.makedirs("data",exist_ok=True)
filename = "data/btn_timings.csv"
try:
    while True:
        current_state = GPIO.input(btn)
        
        #buttonpressed
        
        

        if current_state == GPIO.LOW and previous_state == GPIO.HIGH:
            press_start_time = time.time()
            print("Button pressed")
        
        elif current_state == GPIO.HIGH  and previous_state == GPIO.LOW:#knop is heir losgelaten
            if press_start_time is not None:#ishiereeerdereenstartijdo[geslagen]
                press_end_time = time.time()#tijdstipvannumomentknoplosgelaten
                duration = press_end_time - press_start_time#duur
                readable_time = time.strftime("%Y-%m-%d%H:%M:S",time.localtime(press_start_time))#omzettennaareenleesbaretijd
                
                rows.append([readable_time,duration])
                print("Button released - duration:",duration)
                
                press_start_time = None
        
        previous_state = current_state
        time.sleep(0.1)        

except KeyboardInterrupt:
    print("Program Stopped")
    
finally:
    
    with open(filename,"w",newline=" ") as csvfile:
       writer = csv.writer(csvfile)
        
       writer.writerow(["Timestamp","Duration"])
       writer.writerows(rows)   
    
   
        
        
    if rows:
        times = [datetime.strptime(row[0],"%Y-%m-%d%H:%M:%S") for row in rows]
        durations = [row[1] for row in rows]
        
        fig,ax = plt.subplots(figsize=(8,4))
        ax.plot(times,durations,marker='o',linestyle='-',label='Press Duration')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        fig.autofmt_xdate()
        ax.set_xlabel("Time")
        ax.set_ylabel("Duration(s)")
        ax.set_title("Button press durations")
        ax.legend()
        plt.show()
        
    GPIO.cleanup()    
        
      
 
         




