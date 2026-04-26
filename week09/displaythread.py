import threading
from queue import Queue, Empty

class DisplayThread:
    def __init__(self,display):#the display thread for the four digit 7 segment display

        self.display = display#the display to control
        self.queue = Queue()#the queue for the display
        self._stop_event = threading.Event()#the stop event for the display
        self.thread = threading.Thread(target=self._run)#the thread for the display


    def start(self):#starts the display thread
        self.thread.start()    


    def stop(self):#stops the display thread
        self._stop_event.set()
        self.thread.join()

    def put(self,value):#puts the value on the display
        self.queue.put(value)#puts the value on the queue

    def clear(self):#clears the display
        self.queue.put(" ")#puts a space on the queue
        

    def _run(self):#runs the display thread
        while not self._stop_event.is_set():#runs while the stop event is not set
            try:
                new_value = self.queue.get_nowait()#gets the new value from the queue
                self.display.putValue(new_value)#puts the new value on the display
            except Empty:#if the queue is empty
                pass    

            self.display.refresh_once()#refreshes the display once
                
        