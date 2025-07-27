import pyqtgraph as pg
import os

from PyQt6.QtWidgets import QMainWindow,QApplication
from PyQt6 import uic
from PyQt6.QtCore import QTimer


import math   


class mainwindow(QMainWindow):
    def __init__(self,function):
        super().__init__()
        ui_path=os.path.join(os.path.dirname(__file__),"data_check.ui")
        uic.loadUi(ui_path,self)

        # 大麻設定
        self.timer=QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(1)   

        # 大麻ファンクション
        self.function=function

        # main プロッタ設定
        self.plot1_config=self.main_plot.addPlot()
        self.plot1_config.setXRange(0,500,padding=0)
        self.plot1_data1=self.plot1_config.plot(pen="y")
        self.plot1_data2=self.plot1_config.plot(pen="b")
        self.plot1_data3=self.plot1_config.plot(pen="r")


        
        # プロット設定ボタン
        self.ACCPlotEnable=self.PlotSelectorButton_ACC.toggled.connect(self.PlotSelectorisChanged)
        self.GYRPlotEnable=self.PlotSelectorButton_GYR.toggled.connect(self.PlotSelectorisChanged)
        self.EULPlotEnable=self.PlotSelectorButton_EUL.toggled.connect(self.PlotSelectorisChanged)
        self.PlotDataSelector=0


        
        self.ydash=0
        self.time=0
        self.timedata=[]
        self.data1=[]
        self.data2=[]
        self.data3=[]
    
    # ラジオボタンが変更されたときに実行される関数
    def PlotSelectorisChanged(self):
        if self.PlotSelectorButton_ACC.isChecked():
            self.PlotDataSelector=0
            self.unit_label.setText("[m/s^2]")
        # ジャイロが選択された場合
        if self.PlotSelectorButton_GYR.isChecked():
            self.PlotDataSelector=1
            self.unit_label.setText("[rad/s^2]")
        # オイラー角が選択された場合
        if self.PlotSelectorButton_EUL.isChecked():
            self.PlotDataSelector=2
            self.unit_label.setText("[deg]")

    
    def SetPlotData(self,plotdata):
        self.timedata.append(self.time)
        self.data1.append(plotdata[self.PlotDataSelector][0])
        self.data2.append(plotdata[self.PlotDataSelector][1])
        self.data3.append(plotdata[self.PlotDataSelector][2])
        self.plot1_data1.setData(self.timedata[-500:],self.data1[-500:])
        self.plot1_data2.setData(self.timedata[-500:],self.data2[-500:])
        self.plot1_data3.setData(self.timedata[-500:],self.data3[-500:])
    
    def GetStatusColor(self,Status):
        if Status=="WORKING":
            return "color: blue;"
        if Status=="ERROR":
            return "color: red;"
        if Status=="READY":
            return "color: green;"
    
    def CheckSelectMode(self):
        CameraMode=self.CameraModeSelector.currentText()
        ControlMode=self.ControlModeSelector.currentText()

        return [CameraMode,ControlMode]
    
    def CheckPIDGain(self):
        Kp=[self.KpRoll.value(),self.KpPitch.value(),self.KpYaw.value()]
        Ki=[self.KiRoll.value(),self.KiPitch.value(),self.KiYaw.value()]
        Kd=[self.KdRoll.value(),self.KdPitch.value(),self.KdYaw.value()]

        return [*Kp,*Ki,*Kd]

    
    def SetStatusData(self,plotdata):
        # 色変更＋データ表示
        self.Socket_Status.setStyleSheet(self.GetStatusColor(plotdata[0].get_emptychck()))
        self.Socket_Status.setText(plotdata[0].get_emptychck())

        self.IMU_Status.setStyleSheet(self.GetStatusColor(plotdata[1].get_emptychck()))
        self.IMU_Status.setText(plotdata[1].get_emptychck())

        self.Thrust_Status.setStyleSheet(self.GetStatusColor(plotdata[2].get_emptychck()))
        self.Thrust_Status.setText(plotdata[2].get_emptychck())

        self.Servo_Status.setStyleSheet(self.GetStatusColor(plotdata[3].get_emptychck()))
        self.Servo_Status.setText(plotdata[3].get_emptychck())

        self.Chusyaki_Status.setStyleSheet(self.GetStatusColor(plotdata[4].get_emptychck()))
        self.Chusyaki_Status.setText(plotdata[4].get_emptychck())
        
        self.Camera_Status.setStyleSheet(self.GetStatusColor(plotdata[5].get_emptychck()))
        self.Camera_Status.setText(plotdata[5].get_emptychck())
        
        self.Control_Status.setStyleSheet(self.GetStatusColor(plotdata[6].get_emptychck()))
        self.Control_Status.setText(plotdata[6].get_emptychck())
    
    def CheckThrustDirection_CCW(self,input):
        if input<1600:
            return int(input*(-1))
        return -1600
    
    def CheckThrustDirection_CW(self,input):
        if input>1600:
            return int(input)
        return 1600


    def PlotThrustInputData(self,Input):
        self.Th1Input_parcent_CCW.setValue(self.CheckThrustDirection_CCW(Input[0]))
        self.Th1Input_parcent_CW.setValue(self.CheckThrustDirection_CW(Input[0]))
       
        self.Th2Input_parcent_CCW.setValue(self.CheckThrustDirection_CCW(Input[1]))
        self.Th2Input_parcent_CW.setValue(self.CheckThrustDirection_CW(Input[1]))

        self.Th3Input_parcent_CCW.setValue(self.CheckThrustDirection_CCW(Input[2]))
        self.Th3Input_parcent_CW.setValue(self.CheckThrustDirection_CW(Input[2]))

        self.Th4Input_parcent_CCW.setValue(self.CheckThrustDirection_CCW(Input[3]))
        self.Th4Input_parcent_CW.setValue(self.CheckThrustDirection_CW(Input[3]))
 



    def update(self):
        StatusData,SensData,PropoData,InputData=self.function()
        self.SetPlotData(SensData)
        self.SetStatusData(StatusData)
        self.PlotThrustInputData(InputData)
        print(InputData)

        


        self.time+=1
        if self.time>500:
            self.plot1_config.setXRange(self.time-500,self.time+50,padding=0)



        




