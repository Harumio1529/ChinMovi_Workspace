import sys
import os

# ライブラリインポート
import socket,time,pickle,math
# GUI関連
from PyQt6.QtWidgets import QApplication
import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow,QApplication
from PyQt6 import uic
from PyQt6.QtCore import QTimer

# 自作ライブラリ
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from lib.propo.Propo import ps4
from lib.gui.plot import mainwindow

# 通信用顧問
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import COMMON
# 通信チェック
RasPi_IP,PC_IP=COMMON.CheckIPAddress("PC")

#コントローラー初期化
propo=ps4()
PropoData=[0]*4

# UDP通信クライアント設立
ComAgent=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
ComAgent.bind((PC_IP,COMMON.PCPort))


def Com_main():
    global PropoData
    try:
        data,addr=ComAgent.recvfrom(1024)
        PropoData=propo.getPropoData()
        ComAgent.sendto(pickle.dumps(PropoData),(RasPi_IP,COMMON.RasPiPort))
    
    except socket.timeout:
        pass
    print(data)



COMMON.scheduler(0.001,Com_main)



lasttime=0
# メイン制御部
def main_worker():
    message=1
    # センサ値取得
    # data,addr=client.recvfrom(1024)
    # sensorData=pickle.loads(data)
    # print(sensorData)
    # コントローラ値取得
    # PropoData=propo.getPropoData()
    # ECUノードへ送信
    # SendData=pickle.dumps(PropoData)
    # client.sendto(SendData,ECU.addres)
    # print(PropoData)
    # return sensorData




         
# app=QApplication([])
# main=mainwindow(main_worker)
# main.show()
# app.exec()    
        




