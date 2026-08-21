from ble import bluetooth_uart_server#importing the bluetooth uart server
import threading#importing the threading library
import queue#importing the queue library
import time#importing the time library

rx_q = queue.Queue()#setting the rx queue
tx_q = queue.Queue()#setting the tx queue

threading.Thread(target=bluetooth_uart_server.ble_gatt_uart_loop, args=(rx_q, tx_q, "pjs-rpi-PM"), daemon=True).start()

try:
    while True:#starting the while loop
        try:
            incoming = rx_q.get_nowait()#getting the incoming message
        except queue.Empty:#checking if the queue is empty
            incoming = None#setting the incoming message to none

        if incoming:#checking if the incoming message
            print("Incoming: {}".format(incoming))#printing the incoming message
            tx_q.put("hello back")#putting the outgoing message

        time.sleep(1)#waiting for 1 second
except KeyboardInterrupt:#keyboard interrupt
    print("Ctrl-C received, shutting down...")#printing the interrupt
    bluetooth_uart_server.stop_ble_gatt_uart_loop()#stopping the bluetooth uart loop
    time.sleep(0.5)#waiting for 0.5 seconds  
    