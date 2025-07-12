# 標準ライブラリをimport
import sys ,os
import socket,time,pickle,smbus,threading,queue

# 自作ライブラリをimport
from lib.icm20948.ICM20948 import ICM20948
from lib.madgwickfilter.madgwickahrs import MadgwickAHRS
from lib.PCA9685.pca9685 import PCA9685,THRUSTER,SERVO
from lib.tb6612.tb6612 import TB6612


#デバッグモード
DEBUG_MODE=False 

# Queueデータの箱を準備する
SensorData=queue.Queue()
PropoData=queue.Queue()



#### 通信スレッド用関数 ####
def Com_Thred(ComAgent: socket.socket):
    COMMON.scheduler(0.01,lambda: Com_Thred_main(ComAgent))

# 通信スレッド用main関数
def Com_Thred_main(ComAgent: socket.socket):
    global STSOCKET,STIMU,STTHRUST,STSERVO,STCHU,SA
    # 送信用データまとめ
    # 送信用データの中身([byte])
    # [ACC_X(4),ACC_Y(4),ACC_Z(4),GYR_X(4),GYR_Y(4),GYR_Z(4),PITCH(4),ROLL(4),YAW(4),STSOCKET(1),STIMU(1),STTHRUST(1),STSERVO(1),STCHU(1)]
    # ステータス信号のエンコード
    EncodeStatus=SA.Encoder([STSOCKET,STIMU,STTHRUST,STSERVO,STCHU])
    # センサデータをぶち込む
    if STIMU!="WORKING":
        SendData=[0.0,0.0,0.0,
                        0.0,0.0,0.0,
                        0.0,0.0,0.0,
                        *EncodeStatus]
    else :
        SendData=[*SensorData.get(),*EncodeStatus]
    
    # データのバイナリ化
    SendDataBin=pickle.dumps(SendData)
    # データの送信
    ComAgent.sendto(SendDataBin,(PC_IP,COMMON.PCPort))

    

    # # データ受信
    try:
        RecvData,Fromaddr=ComAgent.recvfrom(1024)
        PropoData.put(pickle.loads(RecvData))

    except socket.timeout:
        STSOCKET="TIMEOUT"
        print("timeout")

def Module_Thred():
    COMMON.scheduler(0.01,Module_Thred_main)

def Module_Thred_main():
    data=PropoData.get()[0]
    input=int(2048+(data*2047))
    input_th=int(1600+(data*600))
    print(input)
    SRV.set_servo(input,input)
    TH.set_thrust(input_th,input_th,input_th,input_th)









# 各種ステータス
STSOCKET="PREPARING"
STIMU="PREPARING"
STTHRUST="PREPARING"
STSERVO="PREPARING"
STCHU="PREPARING"

# socket用アドレスファイルをimport
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import COMMON
# ステータスのデコーダを準備する。
SA=COMMON.StatusAnalyzer()

# i2cモジュール立ち上げ
i2c=smbus.SMBus(1)

# デバッグモードの時はダミーIPアドレスを使う
if DEBUG_MODE:
    RasPI_IP="0.0.0.0"
    PC_IP="0.0.0.0"

else:
    PC_IP,RasPI_IP=COMMON.CheckIPAddress("RaspberryPi")

STSOCKET="COM_OK"

# COMエージェント立ち上げ
STSOCKET="STANDUP_COMAGENT"
ComAgent=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ComAgent.settimeout(0.005)
ComAgent.bind((RasPI_IP, COMMON.RasPiPort))
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
STIMU=IMU.calibration(1)
# 姿勢角推定
EST=MadgwickAHRS(sampleperiod=0.01,beta=1.0)
STIMU="READY"
print("IMU and Estimation is READY !")

# スラスタモジュール起動
TH=THRUSTER(i2c,0,1,2,3)
# キャリブレーション
STTHRUST="CALIBRATION"
STTHRUST=TH.Calibration()
TH.set_thrust(1600,1600,1600,1600)
time.sleep(1)
STTHRUST="READY"
print("THRUSTER is READY !")

# サーボモジュール起動
SRV=SERVO(i2c,8,9)
# キャリブレーション（と言ってるが動かしてるだけ）
STSERVO="CARIBRATION"
STSERVO=SRV.Caribration()
time.sleep(1)
STSERVO="READY"
print("SERVO is READY !")

# チュウシャキモジュール起動
CHU1=TB6612(i2c,PCA9685,7,20,21,LimitEnable=False)
CHU2=TB6612(i2c,PCA9685,6,12,16,LimitEnable=False)
# キャリブレーション(と言ってるが動かしてるだけ)
STCHU="CARIBRATION"
STCHU=CHU1.caribration()
if CHU1.caribration()=="CARIBRATION_OK" and CHU1.caribration()=="CARIBRATION_OK":
    STCHU="CARIBRATION_OK"

STCHU="READY"
print("CHUSYAKI is READY !")
time.sleep(2)


threading.Thread(target=Com_Thred,args=(ComAgent,),daemon=True).start()
threading.Thread(target=Module_Thred,daemon=True).start()

try:
    while True:
        pass
except KeyboardInterrupt:
    TH.close()
    SRV.close()
    CHU.close()

