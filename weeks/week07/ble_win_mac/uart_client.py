"""
UART Service
-------------

An example showing how to write a simple program using the Nordic Semiconductor
(nRF) UART service.

"""

import asyncio# importing the asyncio library
import sys# importing the sys library
from itertools import count, takewhile# importing the count and takewhile functions from the itertools library
from typing import Iterator# importing the Iterator function from the typing library

from bleak import BleakClient, BleakScanner# importing the BleakClient and BleakScanner classes from the bleak library
from bleak.backends.characteristic import BleakGATTCharacteristic# importing the BleakGATTCharacteristic class from the bleak.backends.characteristic module
from bleak.backends.device import BLEDevice# importing the BLEDevice class from the bleak.backends.device module
from bleak.backends.scanner import AdvertisementData# importing the AdvertisementData class from the bleak.backends.scanner module

UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"# setting the UART service UUID
UART_RX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"# setting the UART RX characteristic UUID
UART_TX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"# setting the UART TX characteristic UUID


# TIP: you can get this function and more from the ``more-itertools`` package.
def sliced(data: bytes, n: int) -> Iterator[bytes]:# slices the data into chunks of size n
    """
    Slices *data* into chunks of size *n*. The last slice may be smaller than
    *n*.
    """
    return takewhile(len, (data[i : i + n] for i in count(0, n)))# returns the chunks of data


async def uart_terminal():# defining the uart terminal function
    """This is a simple "terminal" program that uses the Nordic Semiconductor
    (nRF) UART service. It reads from stdin and sends each line of data to the
    remote device. Any data received from the device is printed to stdout.
    """

    def match_nus_uuid(device: BLEDevice, adv: AdvertisementData):# matching the NUS UUID
        # print("found device: {}".format(device.name))# printing the device name
        # This assumes that the device includes the UART service UUID in the# This assumes that the device includes the UART service UUID in the
        # advertising data. This test may need to be adjusted depending on the# advertising data. This test may need to be adjusted depending on the
        # actual advertising data supplied by the device.
        if UART_SERVICE_UUID.lower() in adv.service_uuids:# checking if the UART service UUID is in the advertising data
            return True

        return False

    device = await BleakScanner.find_device_by_filter(match_nus_uuid)# finding the device by filtering the NUS UUID

    if device is None:
        print("no matching device found, you may need to edit match_nus_uuid().")# printing the error message if the device is not found
        sys.exit(1)# exiting the program

    def handle_disconnect(_: BleakClient):# handling the disconnect event
        print("Device was disconnected, goodbye.")# printing the disconnect message
        # cancelling all tasks effectively ends the program
        for task in asyncio.all_tasks():# cancelling all tasks
            task.cancel()

    def handle_rx(_: BleakGATTCharacteristic, data: bytearray):# handling the rx event
        print("received:", data)# printing the received data

    async with BleakClient(device, disconnected_callback=handle_disconnect) as client:# setting the client
        await client.start_notify(UART_TX_CHAR_UUID, handle_rx)# starting the notification

        print("Connected, start typing and press ENTER...")# printing the connected message

        loop = asyncio.get_running_loop()
        nus = client.services.get_service(UART_SERVICE_UUID)# getting the service
        rx_char = nus.get_characteristic(UART_RX_CHAR_UUID)# getting the characteristic

        while True:
            # This waits until you type a line and press ENTER.
            # A real terminal program might put stdin in raw mode so that things
            # like CTRL+C get passed to the remote device.
            data = await loop.run_in_executor(None, sys.stdin.buffer.readline)# getting the data from the user

            # data will be empty on EOF (e.g. CTRL+D on *nix)
            if not data:
                break# breaking the loop if the data is empty

            # some devices, like devices running MicroPython, expect Windows
            # line endings (uncomment line below if needed)
            # data = data.replace(b"\n", b"\r\n")

            # Writing without response requires that the data can fit in a
            # single BLE packet. We can use the max_write_without_response_size
            # property to split the data into chunks that will fit.

            for s in sliced(data, rx_char.max_write_without_response_size):# iterating through the data
                await client.write_gatt_char(rx_char, s, response=False)# writing the data to the characteristic

            print("sent:", data)# printing the sent data


if __name__ == "__main__":# running the main function
    try:
        asyncio.run(uart_terminal())# running the uart terminal
    except asyncio.CancelledError:# handling the cancel error
        # task is cancelled on disconnect, so we ignore this error
        pass