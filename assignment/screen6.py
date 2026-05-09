import smbus#import smbus to communicate with the lcd
import time#import time to wait for the lcd
import threading#import threading to run the ble gatt uart loop in a separate thread
import queue#import queue to pass data between threads
from ble.bluetooth_uart_server import ble_gatt_uart_loop#import the ble gatt uart loop function

# LCD Settings
I2C_ADDR = 0x27#this is the address of the lcd
LCD_WIDTH = 16#this is the width of the lcd
LCD_CHR = 1#this is the character mode of the lcd
LCD_CMD = 0#this is the command mode of the lcd

LCD_LINE_1 = 0x80#this is the first line of the lcd
LCD_LINE_2 = 0xC0#this is the second line of the lcd

ENABLE = 0b00000100#this is the enable pin of the lcd

bus = smbus.SMBus(1)#this is the i2c bus of the lcd

# BLE queues
rx_q = queue.Queue()   # incoming BLE messages
tx_q = queue.Queue()   # outgoing BLE messages
device_name = "pj-pi-gatt-uart"#this is the name of the device that will be broadcasted


def lcd_toggle_enable(bits):# toggle enable pin to write data to the lcd
    time.sleep(0.0005)# wait a tiny bit 
    bus.write_byte(I2C_ADDR, bits | ENABLE)#set enable high
    time.sleep(0.0005)
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)#set enable low
    time.sleep(0.0005)


def lcd_send_byte(bits, mode):# send a byte to the lcd
    high_bits = mode | (bits & 0xF0) | 0x08#send the upper 4 bits of the byte
    low_bits = mode | ((bits << 4) & 0xF0) | 0x08#send the lower 4 bits of the byte

    bus.write_byte(I2C_ADDR, high_bits)#send the upper 4 bits of the byte to the lcd
    lcd_toggle_enable(high_bits)#toggle the enable pin to write the upper 4 bits of the byte to the lcd

    bus.write_byte(I2C_ADDR, low_bits)#send the lower 4 bits of the byte to the lcd
    lcd_toggle_enable(low_bits)#toggle the enable pin to write the lower 4 bits of the byte to the lcd


def lcd_init():#initialize the lcd
    lcd_send_byte(0x33, LCD_CMD)#function set 8 bit mode
    lcd_send_byte(0x32, LCD_CMD)#function set 8 bit mode                                           
    lcd_send_byte(0x06, LCD_CMD)#entry mode set increment cursor                                              
    lcd_send_byte(0x0C, LCD_CMD)#display on cursor off blink off       
    lcd_send_byte(0x28, LCD_CMD)#function set 4 bit mode 2 lines 5x8 dots                                              
    lcd_send_byte(0x01, LCD_CMD)
    time.sleep(0.002)


def lcd_string(message, line):#display a string on the lcd
    message = message.ljust(LCD_WIDTH, " ")#pad the message with spaces to the width of the lcd
    lcd_send_byte(line, LCD_CMD)#set the cursor to the line we want to write to

    for ch in message[:LCD_WIDTH]:
        lcd_send_byte(ord(ch), LCD_CHR)#convert each character to its ascii value and send it to the lcd


def lcd_clear():#clear the lcd
    lcd_send_byte(0x01, LCD_CMD)#clear the lcd                                              
    time.sleep(0.002)


def wait_or_stop(stop_event, seconds):#wait for the stop event to be set
    steps = int(seconds / 0.1)#calculate the number of steps to wait

    for _ in range(steps):#loop through the steps
        if stop_event.is_set():#check if the stop event is set
            return
        time.sleep(0.1)#wait for 0.1 seconds


def run(stop_event):#run the program
    lcd_init()#initialize the lcd
    lcd_clear()#clear the lcd

    lcd_string("Send a message", LCD_LINE_1)#display the message on the lcd
    lcd_string("via BLE UART", LCD_LINE_2)#display the message on the lcd

    ble_thread = threading.Thread(#create a thread to run the ble gatt uart loop
        target=ble_gatt_uart_loop,#target is the function to run in the thread
        args=(rx_q, tx_q, device_name),#arguments to pass to the function
        daemon=True#set as a daemon thread so it will close when the main thread closes without daemon True the prigram will get stuck in the ble gatt uart loop when the user presses ctrl c it would nevver fully exit even after ctrl + c is pressed you would have   to force kill it
    )
    ble_thread.start()#start the thread

    while not stop_event.is_set():#run until the stop event is set
        try:
            incoming = rx_q.get(timeout=0.1)#get the incoming message from the queue

            if isinstance(incoming, (bytes, bytearray)):#check if the incoming message is bytes or bytearray
                incoming = incoming.decode("utf-8", errors="ignore").strip()#decode the incoming message from bytes to a string and remove any leading or trailing whitespace
            else:
                incoming = str(incoming).strip()#convert the incoming message to a string and remove any leading or trailing whitespace

            line1 = incoming[:16]#get the first 16 characters of the message
            line2 = incoming[16:32]#get the next 16 characters of the message

            lcd_clear()#clear the lcd
            lcd_string(line1, LCD_LINE_1)#display the first line of the message
            lcd_string(line2, LCD_LINE_2)#display the second line of the message

        except queue.Empty:
            pass#do nothing if the queue is empty

        wait_or_stop(stop_event, 0.1)#wait for the stop event to be set

    lcd_clear()#clear the lcd


if __name__ == "__main__":
    stop_event = threading.Event()#create an event to stop the thread

    try:
        run(stop_event)#run the program
    except KeyboardInterrupt:#if the user presses ctrl+c
        stop_event.set()#set the stop event
        lcd_clear()#clear the lcd