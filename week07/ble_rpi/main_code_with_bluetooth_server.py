import threading#importing the threading library
import queue#importing the queue library

from ble.bluetooth_uart_server import ble_gatt_uart_loop#importing the bluetooth uart server
def main():
    i = 0#setting the i variable to 0
    rx_q = queue.Queue()#setting the rx queue
    tx_q = queue.Queue()#setting the tx queue
    device_name = "pj-pi-gatt-uart"#setting the device name
    threading.Thread(target=ble_gatt_uart_loop, args=(rx_q, tx_q, device_name), daemon=True).start()#starting the thread
    while True:#starting the while loop
        try:
            incoming = rx_q.get(timeout=1) # Wait for up to 1 second
            if incoming:#checking if the incoming message
                print("In main loop: {}".format(incoming))
        except Exception as e:
            pass # nothing in Q

        if i % 5 == 0: # Send some data every 5 iterations
            tx_q.put("test{}".format(i))#putting the outgoing message
        i += 1#incrementing the i variable

if __name__ == '__main__':
    main()#running the main function