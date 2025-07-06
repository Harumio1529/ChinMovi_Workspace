from multiprocessing import Process,Queue,Value,Lock
import time

def Process1(v,lock):
    i=0.0
    while True:
        with lock:
            # start=time.time()
            i+=0.1
            v.value=i
            # end=time.time()
            # i+=(end-start)
            
        time.sleep(0.1)

            
        
        


def Process2(v,lock):
    while True:
        with lock:
            print(v.value)
        time.sleep(3)


if __name__=="__main__":
    v=Value("d",0.0)
    lock=Lock()
    p1=Process(target=Process1,args=(v,lock,))
    p1.daemon=True
    p2=Process(target=Process2,args=(v,lock,))
    p2.daemon=True

    p1.start()
    p2.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("fin")