import socket
import time
import pickle
from ADDRES import Sensor_node,PC_node

from lib/icm20948 import icm20948

NodeAddres=Sensor_node()
PC=PC_node()

# UDP通信クライアント設立
client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client.bind(NodeAddres.addres)

def main_worker():
    # センサ値取得
    data=[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    # PCへ送信
    Send_Data=pickle.dumps(data)
    client.sendto(Send_Data,PC.addres)

# 定周期大麻
def scheduler(interval, func):
    base_time = time.time()
    next_time = 0
    while True:
        func()
        next_time = ((base_time - time.time()) % interval) or interval
        time.sleep(next_time)


scheduler(0.01,main_worker)