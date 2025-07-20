# GUI関連
from PyQt6.QtWidgets import QApplication
import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow,QApplication
from PyQt6 import uic
from PyQt6.QtCore import QTimer

# 自作ライブラリをimport
from lib.gui.plot import mainwindow
app=QApplication([])

def gui_start(func):
    main=mainwindow(func)
    main.show()
    app.exec()

def gui_fin():
    app.quit()

