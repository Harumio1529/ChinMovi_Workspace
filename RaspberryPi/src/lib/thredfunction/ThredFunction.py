import time
import socket,queue

# 定周期大麻
# interval -> 実行周期[s]
# func -> 実行関数
def scheduler(interval, func):
    base_time = time.time()
    next_time = 0
    while True:
        func()
        next_time = ((base_time - time.time()) % interval) or interval
        time.sleep(next_time)

# 通信スレッド用関数
def Com_Thred(ComAgent):
    