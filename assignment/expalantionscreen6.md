the goal of this exercise is to use Bluetooth functionality so we can receive messages and display letters and numbers on the LCD screen. First we import the libraries we need, these are smbus for i2c communication, time for delays, threading for multithreading, queue for thread communication, and ble.bluetooth_uart_server for the bluetooth uart functionality. #from ble.bluetooth_uart_server import ble_gatt_uart_loop for the bluetooth uart functionality.   

Next we define the lcd settings, these are the address of the lcd, the width of the lcd, the character mode, the command mode, the first line, the second line, the enable pin, and the register select pin. #I2C_ADDR  = 0x27  #address of the lcd.

Then we initialize the i2c bus. #bus = smbus.SMBus(1)  #initialize the i2c bus.
We define the function lcd_toggle_enable which toggles the enable pin of the lcd. #lcd_toggle_enable(bits) #toggle the enable pin. so it reads the data that is being sent to it.

we define a function lcd_send_byte which sends a byte to the lcd. #lcd_send_byte(bits, mode) #send the byte to the lcd. one byte to the LCD in 4-bit mode.


we define a function lcd_init which initializes the lcd. #lcd_init() #initialize the lcd. before displaying anything. to print anything on the lcd we need to initialize it.

we define a function lcd_string which sends a string to the lcd. #lcd_string(message, line) #send the string to the lcd. tgis is used to clear the lcd and display a message on the lcd.

we define a queue rx_q which is used to store incoming data from ble. #rx_q = queue.Queue() #queue to store incoming data from ble. This is used to store messages taht are sent from the phone to the pi.

we define a queue tx_q which is used to store outgoing data to ble. #tx_q = queue.Queue() #queue to store outgoing data to ble. This is used to store data tgar the raspberry pi would send back over Bluetooth.

we define the name of the ble device using the variable device_name. #device_name = "pj-pi-gatt-uart"  #name of the ble device. this is used to identify the device when connecting to it. 

then we define the main function. #def main(): #main function.  of the program

inside the main fucntion m, we initialize the lcd and clear it. #lcd_init() #initialize the lcd. lcd_clear() #clear the lcd. 

then we display a default message on the lcd to tell the user what to do. #lcd_string("Send a message", LCD_LINE_1) #display the message on the lcd. lcd_string("Via BLE UART",   LCD_LINE_2) #display the message on the lcd.

Next we start the ble thread. #threading.Thread(target=ble_gatt_uart_loop, args=(rx_q, tx_q, device_name), daemon=True).start() #start the ble thread.  this is used to sart the blutooth uart loop in the background so the main program can keep running at the same time. threading.Thread is used to create a new thread. daemon=True is used to make the thread a daemon thread. this means that the thread will exit when the main thread exits. args is used to pass arguments to the function that is being run in the thread. target is used to specify the function that is being run in the thread. .start() is used to start the thread.

This means the target function is ble_gatt_uart_loop, the arguments are rx_q, tx_q, and device_name, the thread is a daemon thread, and it is started. pass the receive queue, the transmit queue, and the device name to the function.  it automatically starts the ble server and listens for incoming connections. it automatically stops when the main thread exits.

Then we enter a while loop. #while True: #while loop.  this is used to keep the program running until the user stops it. incoming data from BLE.

inside the while loop,we  get the incoming data from the queue using : #incoming = rx_q.get(timeout=0.1) #get the incoming data from the queue. timeout is used to specify how long to wait for the data. if the data is not received within the timeout period, the program will continue to run. 


if there is incoming data,we decode it and display it on the lcd. #if incoming: #if there is incoming data.  this is used to check if there is incoming data.  if there is incoming data, we decode it and display it on the lcd.  if there is no incoming data, we do nothing.  incoming = incoming.decode("utf-8", errors="ignore").strip() #decode the incoming data from bytes or bytearray format to string.  this is used to decode the incoming data from bytes or bytearray format to string.  errors="ignore" is used to ignore any errors that may occur during the decoding process.  strip() is used to remove any leading or trailing whitespace from the decoded data.  
if incoming:
    if isinstance(incoming, (bytes, bytearray)):
        incoming = incoming.decode("utf-8", errors="ignore").strip()

    line1 = incoming[:16]
    line2 = incoming[16:32]

    lcd_clear()
    lcd_string(line1, LCD_LINE_1)
    lcd_string(line2, LCD_LINE_2)

this part first checks if there is actually a mesage. Then it checks if the message is in bytes or bytearry format.if that is is the case,it decodes the message to a normal string using .decode("utf-8", errors="ignore").strip().  errors="ignore" is used to ignore any errors that may occur during the decoding process.  strip() is used to remove any leading or trailing whitespace from the decoded data.   then it splits the message into two lines and displays it on the lcd. #line1 = incoming[:16] #line1 is the first 16 characters of the message.  line2 = incoming[16:32] #line2 is the next 16 characters of the message.  lcd_clear() #clear the lcd.  lcd_string(line1, LCD_LINE_1) #display the first line on the lcd.  lcd_string(line2, LCD_LINE_2) #display the second line on the lcd.  

if there is no incoming data a queue.Empty exception is raised. #except queue.Empty: #if there is no incoming data.  this is used to catch the exception that is raised when there is no incoming data.  if there is no incoming data, we do nothing.  pass #do nothing.  this is used to pass the exception and continue to run the program.  

if the user presses the exit button on the app, the program will exit. #except KeyboardInterrupt: #if the user presses the exit button on the app.  this is used to catch the exception that is raised when the user presses the exit button on the app.  if the user presses the exit button on the app, we do nothing.  pass #do nothing.  this is used to pass the exception and continue to run the program.  


full logic of this exercise is:
start the LCD, clear it, and display a default message on it.  start the ble thread.  wait for incoming data from ble.  if there is incoming data, decode it and display it on the lcd.  if there is no incoming data, do nothing.  if the user presses the exit button on the app, the program will exit.


















