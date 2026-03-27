from ble import bluetooth_uart_server#
import threading
import queue#
import time

rx_q = queue.Queue()
tx_q = queue.Queue()

threading.Thread(target=bluetooth_uart_server.ble_gatt_uart_loop, args=(rx_q, tx_q, "pjs-rpi-PM"), daemon=True).start()

try:
    while True:
        try:
            incoming = rx_q.get_nowait()
        except queue.Empty:
            incoming = None

        if incoming:
            print("Incoming: {}".format(incoming))
            tx_q.put("hello back")

        time.sleep(1)
except KeyboardInterrupt:
    print("Ctrl-C received, shutting down...")
    bluetooth_uart_server.stop_ble_gatt_uart_loop()
    time.sleep(0.5)
    