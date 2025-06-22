import sys
import os

# ライブラリインポート
import socket
import time
import pickle
import math 
# GUI関連
from PyQt6.QtWidgets import QApplication
import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow,QApplication
from PyQt6 import uic
from PyQt6.QtCore import QTimer


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from lib.propo.Propo import ps4
from lib.gui.plot import mainwindow


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
from ADDRES import Sensor_node,Camera_node,Controler_node,PC_node







#登場するノードを定義
Sensor=Sensor_node()
Camera=Camera_node()
ECU=Controler_node()
PC=PC_node()

#コントローラー初期化
# propo=Propo.ps4()
# PropoData=[0]*4

# UDP通信クライアント設立
# client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
# client.bind(PC.addres)

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




         
app=QApplication([])
main=mainwindow(main_worker)
main.show()
app.exec()    
        




