 Q: Why do you send data in two nibbles?                                       
  A: The LCD only has 4 data pins wired, so one byte (8 bits) must be split into
   two 4-bit chunks — high nibble first, then low nibble.                       
                                                                                
  ---                                                                           
  Q: Why do you pulse the enable pin for every byte?                          
  A: The LCD only reads data on the falling edge of the enable pin. Without that
   pulse it ignores everything sitting on the data pins entirely.
                                                                                
  ---
  Q: Why is 0x08 OR'd into every byte?                                          
  A: It keeps the backlight transistor on. Without it the display logic works 
  perfectly but the screen goes dark because no light shines through the
  characters.                                                                   
   
  ---                                                                           
  Q: Why are there time.sleep calls in lcd_toggle_enable?                     
  A: The LCD needs time to process signals. Without the delays it tries to latch
   data before you've finished sending it, producing garbage output.
                                                                                
  ---                                                                         
  Q: Why use a threading Event instead of a plain variable to stop the loop?    
  A: A plain variable has no thread-safety guarantee — the other thread might   
  not see the change immediately. A threading Event is specifically designed for
   reliable signaling between threads.                                          
                                                                              
  ---                                    
  Q: What happens if get_ip_addresses crashes?
  A: The script dies, the display freezes on whatever was last shown, and there 
  is no recovery or fallback.
