#import libraries
import smbus                                                                  
import time                                             
import threading                                                              
import queue                                                                  
from ble.bluetooth_uart_server import ble_gatt_uart_loop                      
                                                                                
# LCD Settings                                                                
I2C_ADDR  = 0x27  #address of the lcd                                                           
LCD_WIDTH = 16  #width of the lcd 16 characters per line                                                                
LCD_CHR   = 1  #character mode send a normal character                                           
LCD_CMD   = 0  #command mode send a lcd command                                                                 
LCD_LINE_1 = 0x80  #first line of the lcd
LCD_LINE_2 = 0xC0  #second line of the lcd                                                             
ENABLE    = 0b00000100  #enable pin to toggle the enable pin the lcd so it reads data                                                        
RS        = 0b00000001  #register select pin 0 command mode 1 character mode                 
                                                                                
bus = smbus.SMBus(1)  #initialize the i2c bus                                    
                                                                                
def lcd_toggle_enable(bits):                                                  
    time.sleep(0.0005)  #wait a tiny bit
    bus.write_byte(I2C_ADDR, bits | ENABLE)  #set enable high
    time.sleep(0.0005)  #wait a tiny bit
    bus.write_byte(I2C_ADDR, bits & ~ENABLE)  #set enable low
    time.sleep(0.0005)  #wait a tiny bit
                                                                                
def lcd_send_byte(bits, mode):                                                
    # High bits
    high_bits = mode | (bits & 0xF0) | 0x08 # 0x08 keeps backlight ON
    bus.write_byte(I2C_ADDR, high_bits)  #send the upper 4 bits of the byte
    lcd_toggle_enable(high_bits)  #toggle the enable pin                                              
    
    # Low bits
    low_bits  = mode | ((bits << 4) & 0xF0) | 0x08  #send the lower 4 bits of the byte                            
    bus.write_byte(I2C_ADDR, low_bits)  #send the lower 4 bits of the byte                  
    lcd_toggle_enable(low_bits)                                               
                                                          
def lcd_init():                                                               
    lcd_send_byte(0x33, LCD_CMD)  #function set 8 bit mode
    lcd_send_byte(0x32, LCD_CMD)  #function set 8 bit mode                                              
    lcd_send_byte(0x06, LCD_CMD)  #entry mode set increment cursor                                              
    lcd_send_byte(0x0C, LCD_CMD)  #display on cursor off blink off       
    lcd_send_byte(0x28, LCD_CMD)  #function set 4 bit mode 2 lines 5x8 dots                                              
    lcd_send_byte(0x01, LCD_CMD)  #clear the lcd                                              
    time.sleep(0.0005)  #wait a tiny bit                 
                                                                                
def lcd_string(message, line):                                                
    message = message.ljust(LCD_WIDTH, " ")  #pad the message with spaces to the width of the lcd
    lcd_send_byte(line, LCD_CMD)  #set the cursor to the line we want to write to                                              
    for ch in message[:LCD_WIDTH]:  #loop through the message and send each character to the lcd                                            
        lcd_send_byte(ord(ch), LCD_CHR)  #send the character to the lcd
                                                                                
def lcd_clear():                                                              
    lcd_send_byte(0x01, LCD_CMD)  #clear the lcd       
    time.sleep(0.0005)  #wait a tiny bit                                                        
                                                          
rx_q = queue.Queue()                   #queue to store incoming data from ble
tx_q = queue.Queue()  #queue to store outgoing data to ble
device_name = "pj-pi-gatt-uart"  #name of the ble device                                               
   
def main():                                                                   
    lcd_init()                            #initialize the lcd              
    lcd_clear()                           #clear the lcd                            
    lcd_string("Send a message", LCD_LINE_1)  #display the message on the lcd      
    lcd_string("Via BLE UART",   LCD_LINE_2)  #display the message on the lcd
                                                                                
    threading.Thread(#start the ble thread
        target=ble_gatt_uart_loop,                    #target function                        
        args=(rx_q, tx_q, device_name),               #arguments to the function                        
        daemon=True                    #set as daemon thread so it exits when the main thread exits
    ).start()

    while True:
        try:
            # Check for incoming BLE data
            incoming = rx_q.get(timeout=0.1)  #get the incoming data from the queue
            if incoming:                                     #if there is incoming data                 
                if isinstance(incoming, (bytes, bytearray)):  #check if the incoming data is in bytes or bytearray format
                    incoming = incoming.decode("utf-8", errors="ignore").strip()  #decode the incoming data from bytes or bytearray format to string
                
                # Split text for the two lines
                line1 = incoming[:16]  #split the incoming data into two lines
                line2 = incoming[16:32]  #split the incoming data into two lines
                
                lcd_clear()  #clear the lcd                 
                lcd_string(line1, LCD_LINE_1)  #display the first line on the lcd                                 
                lcd_string(line2, LCD_LINE_2)  #display the second line on the lcd
        except queue.Empty:  #if there is no incoming data                                                   
            continue  #continue to the next iteration                                    
        except KeyboardInterrupt:  #if the user presses ctrl+c
            lcd_clear()  #clear the lcd
            print("\nExiting...")                                               
            break

if __name__ == "__main__":                              
    main()