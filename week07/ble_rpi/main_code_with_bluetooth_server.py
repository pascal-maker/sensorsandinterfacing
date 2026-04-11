import threading
import queue

from ble.bluetooth_uart_server import ble_gatt_uart_loop
def main():
    i = 0
    rx_q = queue.Queue()
    tx_q = queue.Queue()
    device_name = "pj-pi-gatt-uart"
    threading.Thread(target=ble_gatt_uart_loop, args=(rx_q, tx_q, device_name), daemon=True).start()
    while True:
        try:
            incoming = rx_q.get(timeout=1) # Wait for up to 1 second
            if incoming:
                print("In main loop: {}".format(incoming))
        except Exception as e:
            pass # nothing in Q

        if i % 5 == 0: # Send some data every 5 iterations
            tx_q.put("test{}".format(i))
        i += 1

if __name__ == '__main__':
    main()