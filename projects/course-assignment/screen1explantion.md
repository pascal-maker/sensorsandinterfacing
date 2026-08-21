                                             
⏺ LCD IP Address Display Assignment — Summary                                   
                                                                              
  What you built: A Python script that connects a 16×2 LCD (via I2C backpack) to
   your Raspberry Pi's WiFi and ethernet interfaces and cycles between showing
  both IPs on screen every 2 seconds.                                           
                                                                              
  ---                                                                           
  The Hardware
                                                                                
  - LCD: 1602 module — 16 characters × 2 rows, uses HD44780 controller        
  - I2C backpack (PCF8574): converts serial I2C from Pi into parallel signals   
  the LCD needs. Your display is at address 0x27.                               
                                                                                
  ---                                                                           
  The Protocol — Sending One Byte in 4-bit Mode                               
                                                                                
  Each byte must be split into two nibbles because only 4 data pins connect to
  the LCD:                                                                      
                                                                              
  # Extract upper 4 bits, shift lower 4 bits up                                 
  high_bits = mode | (bits & 0xF0) | 0x08   # send top half first               
  low_bits  = mode | ((bits << 4) & 0xF0) | 0x08  # then bottom half            
                                                                                
  bus.write_byte(I2C_ADDR, high_bits)                                           
  lcd_toggle_enable(high_bits)    # ring the bell — LCD reads data              
  bus.write_byte(I2C_ADDR, low_bits)                                            
  lcd_toggle_enable(low_bits)                                                   
                                                                                
  The | 0x08 sets the backlight bit on the PCF8574. Remove it and your display  
  works but screen goes black.                                                  
                                                                                
  The Enable Pulse                                                              
                                         
  The LCD only reads data when enable transitions high→low (falling edge):      
                                                                              
  def lcd_toggle_enable(bits):                                                  
      time.sleep(0.0005)                                                        
      bus.write_byte(I2C_ADDR, bits | ENABLE)  # set high                       
      time.sleep(0.0005)                                                        
      bus.write_byte(I2C_ADDR, bits & ~ENABLE) # set low — falling edge!        
      time.sleep(0.0005)                                                        
                                                                                
  Without this pulse, data sitting on the pins is ignored entirely.             
                                                                                
  ---                                                                           
  Initialization Sequence (the "boot" routine)                                
                                                                                
  The HD44780 spec requires forcing a known state before use:
                                                                                
  lcd_send_byte(0x33, LCD_CMD)   # wake up — send "3" three times to settle     
  lcd_send_byte(0x32, LCD_CMD)   # switch to 4-bit mode                         
  lcd_send_byte(0x06, LCD_CMD)   # cursor increments right                      
  lcd_send_byte(0x0C, LCD_CMD)   # display on, no cursor                        
  lcd_send_byte(0x28, LCD_CMD)   # final config: 4-bit, 2 lines, 5×8 dots       
  lcd_send_byte(0x01, LCD_CMD)   # clear screen (takes up to 1.6ms!)            
  time.sleep(0.002)              # ← increase from 0.0005!                      
                                                                                
  The first two bytes (33, then 32) are what makes this work — they reset the   
  controller regardless of its initial state after power-on. Without them,      
  initialization is flaky.                                                      
                                                                              
  ---                                                                           
  Parsing IP Addresses with subprocess
                                                                                
  def get_ip_addresses():                                                     
      output = subprocess.check_output("ip a", shell=True, text=True)           
      wlan_ip = "Not Connected"                                                 
      eth_ip  = "Not Connected"                                                 
      current_adapter = ""                                                      
                                                                                
      for line in output.splitlines():                                          
          if "wlan0:" in line:      # enter WiFi section                        
              current_adapter = "wlan0"                                         
          elif "eth0:" in line:     # enter LAN section                         
              current_adapter = "eth0"                                          
          elif line.startswith("inet"):  # find the IPv4 address                
              ip_address = line.split()[1].split("/")[0]                        
              if current_adapter == "wlan0":                                    
                  wlan_ip = ip_address                                          
              elif current_adapter == "eth0":                                   
                  eth_ip = ip_address                                           
                                                                                
      return wlan_ip, eth_ip                                                    
                                                                                
  This is a state-machine approach: track which interface you're in, then grab  
  the address from the next inet line.                                        
                                                                                
  ---                                                                           
  The Main Loop with Clean Shutdown      
                                                                                
  def run(stop_event):                                                        
      lcd_init()                                                                
      while not stop_event.is_set():                                            
          wlan_ip, eth_ip = get_ip_addresses()                                  
                                                                                
          # Display WiFi IP                                                     
          lcd_clear()                                                           
          lcd_string("WiFi: ", LCD_LINE_1)                                      
          lcd_string(wlan_ip, LCD_LINE_2)                                       
          wait_or_stop(stop_event, 2)                                           
                                                                                
          if stop_event.is_set():                                               
              break                                                             
                                                                                
          # Display LAN IP                                                      
          lcd_clear()                                                           
          lcd_string("LAN: ", LCD_LINE_1)                                       
          lcd_string(eth_ip, LCD_LINE_2)                                        
          wait_or_stop(stop_event, 2)                                           
                                                                                
      lcd_clear()   # always clean up before exit                               
                                                                                
  if __name__ == "__main__":                                                    
      stop_event = threading.Event()                                          
      try:                                                                      
          run(stop_event)                                                       
      except KeyboardInterrupt:                                                 
          stop_event.set()                                                      
          lcd_clear()                                                           
                                                                                
  The threading.Event pattern is ready for multi-threaded extensions (buttons,  
  sensors). The try/except KeyboardInterrupt ensures Ctrl+C exits cleanly       
  instead of crashing Python and leaving the display blank.                     
                                                                              
  ---                                                                           
  Key Takeaways
                                                                                
  1. 4-bit mode = split every byte into two nibbles because only 4 data pins  
  exist                                                                         
  2. Enable pulse = LCD reads on falling edge (high→low), not continuously    
  3. Initialization sequence matters — 0x33 then 0x32 forces a known state;     
  without it, the display is flaky                                              
  4. Padding with spaces (ljust) prevents garbage from previous messages        
  appearing                                                                     
  5. threading.Event over plain variables for safe cross-thread communication 
  6. Error handling on shutdown — try/except KeyboardInterrupt prevents leaving 
  the LCD in a bad state                                                        

  ---                                                                           
  Imports and setup: At the top I imported smbus2 (to talk to the LCD),
  threading, time, and subprocess. Then I defined constants — the I2C address   
  (0x27), screen width (16), character vs command mode, line addresses for row 1
   and 2, and pin definitions for enable and register select.                   
                                                                              
  Register Select (RS): This pin tells the LCD what kind of data is coming next.
   0 means it's a command to execute; 1 means it's regular text to display.     
  
  Enable: The bell you ring on every byte — toggling this pin lets the LCD know 
  when to read the data sitting on its pins.                                  
                                                                                
  I2C bus initialization: I created the SMBus object pointing at bus 1, which is
   what modern Raspberry Pis use.        
                                                                                
  lcd_toggle_enable(): This function makes the LCD read data by setting enable  
  high, waiting a tiny bit (0.5ms), then bringing it low. The half-millisecond
  delays are critical because the LCD is slow compared to the Pi CPU — without  
  them, the display reads garbage or nothing at all. Each pulse latches data on
  the falling edge (high→low transition).

  lcd_send_byte(): This only works when the enable line is pulsed. It sends data
   in two 4-bit chunks because I2C backpacks only have 4 data lines connected to
   the LCD: first the upper nibble, then the lower one (shifted up by 4         
  positions). The 0x08 bitmask sets the backlight bit — if you remove it, your
  display still works but the screen goes black.

  lcd_init(): The initialization sequence starts with 0x33 and 0x32 to switch   
  from 8-bit mode down to 4-bit mode (required by the spec). Then it sets cursor
   behavior, turns on the display, configures for 2 lines of 5×8 dots, and      
  clears the screen. The half-millisecond sleep after clear is important —    
  clearing takes longer than other operations.

  lcd_string(): I pad messages to 16 characters so previous garbage content gets
   overwritten with spaces, then send each character one by one on its line.
                                                                                
  lcd_clear(): Simple enough — sends command 0x01 to wipe the display.          
                                         
  get_ip_addresses(): The main data function. It imports subprocess to run Linux
   commands (ip a) and parses output by splitting lines, removing whitespace, 
  checking for "wlan0:" or "eth0:", then extracting the IP address from inet    
  lines when found. Default values are "Not Connected" if no interface is     
  active.                                

  wait_or_stop(): Waits for given seconds but checks every 100ms to see if a    
  stop event has been set, so it doesn't block too long.
                                                                                
  run(stop_event): The main loop that initializes the LCD, gets WiFi and LAN    
  IPs, displays them alternating every 2 seconds on lines 1-2 (WiFi) and 1-3
  (LAN), and checks continuously whether to stop. If the event is set, we break 
  cleanly and clear the display.                                              
                                         
  main block: Sets up a threading Event for shutdown signals and wraps          
  everything in try/except KeyboardInterrupt so pressing Ctrl+C exits gracefully
   instead of crashing Python and leaving the LCD blank.                                      