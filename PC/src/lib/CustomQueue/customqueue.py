import queue

class CustomQueue(queue.Queue):
    def __init__(self, init_item,maxsize = 1):
        super().__init__(maxsize)
        self.latchval=init_item
        super().put(init_item)
        


    def get_emptychck(self):
        if not self.empty():
            self.latchval=self.get_nowait()
            self.task_done()
            
        return self.latchval
    
    def put(self,item):
        while not self.empty():
            self.get_nowait()
            self.task_done() 
        self.latchval=item
        super().put(self.latchval)
    
    def peek(self):
        return self.latchval
                
            
