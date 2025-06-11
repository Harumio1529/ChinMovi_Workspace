import pyqtgraph as pg
import os

from PyQt6.QtWidgets import QMainWindow,QApplication
from PyQt6 import uic
from PyQt6.QtCore import QTimer

import math 

class mainwindow(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path=os.path.join(os.path.dirname(__file__),"data_check.ui")
        uic.loadUi(ui_path,self)

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

    def update(self,function):
        function()
        self.x.append(self.time)
        self.y.append(self.ydash)
        self.plot1_data.setData(self.x[-500:],self.y[-500:])
        self.plot2_data.setData(self.x[-500:],self.y[-500:])
        self.plot3_data.setData(self.x[-500:],self.y[-500:])

        self.time+=1
        if self.time>500:
            self.plot1_config.setXRange(self.time-500,self.time+50,padding=0)
            self.plot2_config.setXRange(self.time-500,self.time+50,padding=0)
            self.plot3_config.setXRange(self.time-500,self.time+50,padding=0)

    def set_timer(self,function):
        # 大麻設定
        self.timer=QTimer()
        self.timer.timeout.connect(self.update(function))
        self.timer.start(10)    

def gui_start():
    app=QApplication([])
    main=mainwindow()
    main.show()
    app.exec()    


        




