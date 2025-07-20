import queue


class CustomQueue_withThred(queue.Queue):
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

class CustomQueue_withCoreCom():
    def __init__(self, init_item,maxsize = 1):
        from multiprocessing import Queue
        self.queue=Queue(maxsize=maxsize)
        self.latchval=init_item
        self.queue.put(init_item)
    
    def get_emptychck(self):
        if not self.queue.empty():
            self.latchval=self.queue.get_nowait()
        return self.latchval
    
    def put(self,item):
        while not self.queue.empty():
            self.queue.get_nowait()
        self.latchval=item
        self.queue.put(self.latchval)
    
    def peek(self):
        return self.latchval

    
                
            
