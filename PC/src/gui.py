# GUI関連
from PyQt6.QtWidgets import QApplication
import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow,QApplication
from PyQt6 import uic
from PyQt6.QtCore import QTimer

# 自作ライブラリをimport
from lib.gui.plot import mainwindow
app=QApplication([])
main=None

def gui_start(func):
    global main
    main=mainwindow(func)
    main.show()
    app.exec()

def gui_fin():
    app.quit()

def GetControlModeDatafromGUI():
    global main
    return main.CheckSelectMode()

def GetPIDGainfromGUI():
    global main
    return main.CheckPIDGain()



if __name__=="__main__":
    def function():
        return [[0,0,0],[1,1,1],[2,2,2]]
    gui_start(function)
