# 標準ライブラリをimport
import sys ,os
import socket,time,pickle,smbus

# 自作ライブラリをimport
from lib.icm20948.ICM20948 import ICM20948
from lib.madgwickfilter.madgwickahrs import MadgwickAHRS
from lib.PCA9685.pca9685 import PCA9685,THRUSTER
from lib.tb6612.tb6612 import TB6612

# 各種ステータス
STSOCKET="PREPARING"
STIMU="PREPARING"
STTHRUST="PREPARING"

# socket用アドレスファイルをimport
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import ADDRES

# i2cモジュール立ち上げ
i2c=smbus.SMBus(1)

# 通信チェック
PC_IP=ADDRES.CheckIPAddress("RaspberryPi")
# 通信用アドレスファイルをロード
PC=ADDRES.PC(PC_IP)
STSOCKET="READY"
print("socket com is READY!")

# センサモジュール起動
IMU=ICM20948(i2c)
IMU.hello()
IMU.setup()
# センサ設定
IMU.set_scale_gyr("500dps")
IMU.set_scale_acc("2G")
STIMU="SETUP"
# キャリブレーション
STIMU="CALIBRATION"
IMU.calibration(1000)
# 姿勢角推定
EST=MadgwickAHRS(sampleperiod=0.01,beta=1.0)
STIMU="READY"
print("IMU and Estimation is READY !")

# スラスタモジュール起動
TH=THRUSTER(i2c,0,1,2,3)
# キャリブレーション
STTHRUST="CALIBRATION"
TH.Calibration()
time.sleep(1)
STTHRUST="READY"
print("THRUSTER is READY !")





