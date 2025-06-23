# 標準ライブラリをimport
import sys ,os
# import socket,time,pickle,smbus

# 自作ライブラリをimport
from lib.icm20948.ICM20948 import ICM20948
from lib.madgwickfilter.madgwickahrs import MadgwickAHRS
from lib.PCA9685.pca9685 import PCA9685
# from lib.tb6612.tb6612 import TB6612

# socket用アドレスファイルをimport
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import ADDRES

ADDRES.CheckIPAddress("RaspberryPi")