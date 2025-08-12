import ray
import time
import threading
import math
from multiprocessing import shared_memory
import numpy as np

ray.init()

@ray.remote
class sens:
    def __init__(self,state,name):
        self.omega=0
        self.val=0
        self.state=state
        self.task_run=True
        self.shm=shared_memory.SharedMemory(name=name)
        self.sens_arr=np.ndarray((5,),dtype=np.float32,buffer=self.shm.buf)
        threading.Thread(target=self.sens_task,daemon=True).start()

    def sens_task(self):
        while self.task_run:
            self.omega+=0.01
            self.val=math.sin(self.omega)
            self.sens_arr[:]=np.random.rand(5).astype(np.float32)
            if self.omega>=15:
                self.state.set_status.remote("OKOK")
            time.sleep(0.01)
    
    def get(self):
        return self.omega
    
    
    def stop_task(self):
        self.task_run=False


@ray.remote
class view:
    def __init__(self,sens,state,name):
        self.sens=sens
        self.state=state
        self.task_run=True
        self.shm=shared_memory.SharedMemory(name=name)
        self.sens_arr=np.ndarray((5,),dtype=np.float32,buffer=self.shm.buf)
        threading.Thread(target=self.view_task,daemon=True).start()

    
    def view_task(self):
        while self.task_run:
            val=ray.get(self.sens.get.remote())
            out=val
            self.state.set_time.remote(out)
            if out>=10:
                self.state.set_status.remote("OK")
            print(self.sens_arr)
            time.sleep(0.1)
    
    def stop_task(self):
        self.task_run=False

@ray.remote
class status:
    def __init__(self):
        self.out=0
        self.st="preparing"
        self.task_run=True
        threading.Thread(target=self.status_view,daemon=True).start()
    
    def status_view(self):
        while self.task_run:
            if self.st=="OK":
                o=self.out
                # print(self.out)
            # print(self.st)
            time.sleep(1)
    
    def set_time(self,time):
        self.out=time

    def set_status(self,newstate):
        self.st=newstate
    
    def stop_task(self):
        self.task_run=False

shm = shared_memory.SharedMemory(create=True, size=np.zeros(5, dtype=np.float32).nbytes)
arr = np.ndarray((5,), dtype=np.float32, buffer=shm.buf)

state=status.remote()
sensor=sens.remote(state,shm.name)
output=view.remote(sensor,state,shm.name)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ray.get(sensor.stop_task.remote())
    ray.get(output.stop_task.remote())
    ray.get(state.stop_task.remote())

    shm.close()
    shm.unlink()
    ray.shutdown