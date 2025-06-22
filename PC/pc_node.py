import sys
import os

import socket
import time
import pickle

from PyQt6.QtWidgets import QApplication

from lib import Propo as Propo
from lib.gui import plot

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from ADDRES import Sensor_node,Camera_node,Controler_node,PC_node

import pyqtgraph as pg
import os

from PyQt6.QtWidgets import QMainWindow,QApplication
from PyQt6 import uic
from PyQt6.QtCore import QTimer

import math 

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
    data,addr=client.recvfrom(1024)
    sensorData=pickle.loads(data)
    print(sensorData)
    # コントローラ値取得
    # PropoData=propo.getPropoData()
    # 制御計算
    # motorinput=PID.calc_input(PropoData)
    # ECUノードへ送信
    # SendData=pickle.dumps(PropoData)
    # client.sendto(SendData,ECU.addres)
    # print(PropoData)
    return sensorData



class mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path=os.path.join(os.path.dirname(__file__),"data_check.ui")
        uic.loadUi(ui_path,self)

        # 大麻設定
        self.timer=QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10)   

        # roll プロッタ設定
        self.plot1_config=self.roll_plot.addPlot()
        self.plot1_config.setXRange(0,500,padding=0)
        self.plot1_data=self.plot1_config.plot(pen="y")

        # pitch プロッタ設定
        self.plot2_config=self.pitch_plot.addPlot()
        self.plot2_config.setXRange(0,500,padding=0)
        self.plot2_data=self.plot2_config.plot(pen="y")

        # yaw プロッタ設定
        self.plot3_config=self.yaw_plot.addPlot()
        self.plot3_config.setXRange(0,500,padding=0)
        self.plot3_data=self.plot3_config.plot(pen="y")
        
        self.ydash=0
        self.time=0
        self.x=[]
        self.y=[]

    def update(self):
        plotdata=main_worker()
        self.x.append(self.time)
        self.y.append(plotdata[0])
        self.plot1_data.setData(self.x[-500:],self.y[-500:])
        self.plot2_data.setData(self.x[-500:],self.y[-500:])
        self.plot3_data.setData(self.x[-500:],self.y[-500:])

        self.time+=1
        if self.time>500:
            self.plot1_config.setXRange(self.time-500,self.time+50,padding=0)
            self.plot2_config.setXRange(self.time-500,self.time+50,padding=0)
            self.plot3_config.setXRange(self.time-500,self.time+50,padding=0)

         
app=QApplication([])
main=mainwindow()
main.show()
app.exec()    
        




