import socket
import time
import pickle
import threading

from lib import Propo as Propo
from lib import Controler as Controler
from ADDRES import Sensor_node,Camera_node,Controler_node,PC_node

#登場するノードを定義
Sensor=Sensor_node()
Camera=Camera_node()
ECU=Controler_node()
PC=PC_node()


#コントローラー初期化
propo=Propo.ps4()
PropoData=[0]*4

# PID初期化
PID=Controler.PID_Controler()

# UDP通信クライアント設立
client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

lasttime=0
# メイン制御部
def main_worker():
    global lasttime
    message=1
    # センサ値取得
    # client.sendto(message,(Sensor.IP,Sensor.PORT))
    # data,addr=client.recvfrom(1024)
    # sensorData=pickle.loads(data)
    # コントローラ値取得
    PropoData=propo.getPropoData()
    # 制御計算
    # motorinput=PID.calc_input(PropoData)
    # # ECUノードへ送信
    # SendData=pickle.dumps(motorinput)
    # client.sendto(SendData,(ECU.IP,ECU.PORT))
    now=time.time()
    print(now-lasttime)
    lasttime=now
    

# 定周期大麻
def scheduler(interval, func,wait=True):
    global propo,PropoData
    base_time = time.time()
    next_time = 0
    while True:
        # t = threading.Thread(target = func)
        # t.start()
        func()
        if wait:
            next_time = ((base_time - time.time()) % interval) or interval
            time.sleep(next_time)

    
scheduler(1,main_worker,True)

# while True:
#     try:
        
#         # main_worker()

#     except KeyboardInterrupt:
#         client.close()
#         break