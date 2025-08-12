# 標準ライブラリをimport
import sys ,os
import socket,time,pickle,threading,queue,cv2,ray
from multiprocessing import shared_memory
import time
from datetime import datetime
import numpy as np

# 自作ライブラリをimport
from lib.icm20948.ICM20948 import ICM20948
from lib.madgwickfilter.madgwickahrs import MadgwickAHRS
from lib.PCA9685.pca9685 import PCA9685,THRUSTER,SERVO
from lib.tb6612.tb6612 import TB6612
from lib.CustomQueue.customqueue import CustomQueue_withThred
from lib.Camera.camera import camera
from lib.System import SystemCheck
from lib.MS5837 import ms5837
from lib.sen0599 import sen0599
# コントローラクラス
from controller import Controller

# socket用アドレスファイルをimport
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import COMMON


SystemCheck.wifi_off()


### デバッグモード ###
DEBUG_MODE=False
DEBUG_PRINT=True
CAMERA_ENABLE=False


#デバッグ用コンソール出力
def debugprint(data):
    if DEBUG_PRINT:
        print(data)


ray.init(num_cpus=4)


# ---ステータス、PC通信管理
@ray.remote(num_cpus=1)
class IFManager:
    def __init__(self,sens_memory_name,input_memory_name,propo_memory_name,gain_memory_name,status_memory_name):
        # ステータスのデコーダを準備する。
        self.SA=COMMON.StatusAnalyzer()
        # タスク回転フラグ
        self.task_run=True

        # 共有メモリ
        # センサメモリ
        self.sens_memory=shared_memory.SharedMemory(name=sens_memory_name)
        self.sens_arr=np.ndarray((11,),dtype=np.float32,buffer=self.sens_memory.buf)
        # 入力値メモリ
        self.input_memory=shared_memory.SharedMemory(name=input_memory_name)
        self.input_arr=np.ndarray((8,),dtype=np.float32,buffer=self.input_memory.buf)
        # プロポメモリ
        self.propo_memory=shared_memory.SharedMemory(name=propo_memory_name)
        self.propo_arr=np.ndarray((11,),dtype=np.float32,buffer=self.propo_memory.buf)
        # ゲインメモリ
        self.gain_memory=shared_memory.SharedMemory(name=gain_memory_name)
        self.gain_arr=np.ndarray((9,),dtype=np.float32,buffer=self.gain_memory.buf)
        # ステータスメモリ
        self.status_memory=shared_memory.SharedMemory(name=status_memory_name)
        self.status_arr=np.ndarray((7,),dtype=np.int8,buffer=self.status_memory.buf)
        
        # ステータス
        self.STSOCKET="PREPARING"
        self.STIMU="PREPARING"
        self.STTHRUST="PREPARING"
        self.STSERVO="PREPARING"
        self.STCHU="PREPARING"
        self.STCAMERA="PREPARING"
        self.STCONTROLLER="PREPARING"

        self.set_status_to_sharememory()

        

        # PC通信設定
        # socket用アドレスファイルをimport
        sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))

        # デバッグモードの時はダミーIPアドレスを使う
        if DEBUG_MODE:
            self.RasPI_IP="0.0.0.0"
            self.PC_IP="0.0.0.0"
        else:
            self.PC_IP,self.RasPI_IP=COMMON.CheckIPAddress("RaspberryPi")
        self.set_status("STSOCKET","COM_OK")


        # COMエージェント立ち上げ
        self.set_status("STSOCKET","STANDUP_COMAGENT")
        self.ComAgent=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ComAgent.settimeout(0.05)
        self.ComAgent.bind((self.RasPI_IP, COMMON.RasPiPort))
        self.set_status("STSOCKET","READY")
        debugprint("socket com is READY!")

        threading.Thread(target=self.TimerFunc,daemon=True).start()
    
    def TimerFunc(self):
        print("run")
        COMMON.scheduler(0.1,lambda: self.main_task(),enable=self.task_run)
    
    def stop_task(self):
        self.task_run=False
    
    def set_status_to_sharememory(self):
        STATUS=[
                self.STSOCKET,
                self.STIMU,
                self.STTHRUST,
                self.STSERVO,
                self.STCHU,
                self.STCAMERA,
                self.STCONTROLLER]
        
        EncodedStatus=self.SA.Encoder(STATUS)
        self.status_arr[:]=EncodedStatus
    
    def set_status(self,target,status):
        if target=="STSOCKET":
            self.STSOCKET=status
        elif target=="STIMU":
            self.STIMU=status
        elif target=="STTHRUST":
            self.STTHRUST=status
        elif target=="STSERVO":
            self.STSERVO=status
        elif target=="STCHU":
            self.STCHU=status
        elif target=="STCAMERA":
            self.STCAMERA=status
        elif target=="STCONTROLLER":
            self.STCONTROLLER=status
        else:
            print("Invalid Status Signal")
        
        self.set_status_to_sharememory()
    
    # def get_status(self,target):
    #     print("h")
    #     if target=="STSOCKET":
    #         return self.STSOCKET
    #     elif target=="STIMU":
    #         return self.STIMU
    #     elif target=="STTHRUST":
    #         return self.STTHRUST
    #     elif target=="STSERVO":
    #         return self.STSERVO
    #     elif target=="STCHU":
    #         return self.STCHU
    #     elif target=="STCAMERA":
    #         return self.STCAMERA
    #     elif target=="STCONTROLLER":
    #         return self.STCONTROLLER
    #     else:
    #         print("Invalid Status Signal")

    # プロポのデータを選別する。22→10
    def data_selector(self,data):   
        # 使用データは設計書参照
        return [data[1],data[2],data[3],
                data[4],data[5],
                data[6],data[7],
                data[17],data[18],data[19],data[20]]
    
    # 通信データをステータスとプロポのデータに分ける
    def data_separater(self,data):
        # 前から22個はプロポのデータが入ってくる
        self.propo_arr[:]=self.data_selector(data[:22])
        # そのあと9個はPIDゲインが入ってくる
        self.gain_arr[:]=data[22:31]
        # それより後ろはステータスのデータ
        StatusData=self.SA.Decoder(data[31:])
        if StatusData[0]=="WORKING":
            self.STSOCKET=StatusData[0]
        if StatusData[1]=="WORKING":
            self.STIMU=StatusData[1]
        if StatusData[2]=="WORKING":
            self.STTHRUST=StatusData[2]
        if StatusData[3]=="WORKING":
            self.STSERVO=StatusData[3]
        if StatusData[4]=="WORKING":
            self.STCHU=StatusData[4]
        if StatusData[5]=="SERCH_MODE" or StatusData[5]=="VIDEO_MODE":
            self.STCAMERA=StatusData[5]
        if StatusData[6]!="PREPARING":
            self.STCONTROLLER=StatusData[6]

    def main_task(self):
        # 送信用データまとめ
        # 送信用データの中身([byte])
        # [ACC_X(4),ACC_Y(4),ACC_Z(4),GYR_X(4),GYR_Y(4),GYR_Z(4),PITCH(4),ROLL(4),YAW(4),STSOCKET(1),STIMU(1),STTHRUST(1),STSERVO(1),STCHU(1),STCAMERA(1)]
        # ステータス信号のエンコード
        EncodeStatus=self.SA.Encoder([
                                    self.STSOCKET,
                                    self.STIMU,
                                    self.STTHRUST,
                                    self.STSERVO,
                                    self.STCHU,
                                    self.STCAMERA,
                                    self.STCONTROLLER])

        # センサデータをぶち込む
        if self.STIMU!="WORKING" and self.STTHRUST!="WORKING":
            SendData=[0.0,0.0,0.0,      #加速度
                    0.0,0.0,0.0,      #ジャイロ
                    0.0,0.0,0.0,      #オイラー各
                    0.0,              #超音波センサ
                    0.0,              #深度センサ
                    0.0,0.0,0.0,0.0,  #スラスタ指示値
                    0.0,0.0,          #サーボ指示値
                    *EncodeStatus]
        else :
            GYR=[self.sens_arr[0],self.sens_arr[1],self.sens_arr[2]]
            ACC=[self.sens_arr[3],self.sens_arr[4],self.sens_arr[5]]
            EUL=[self.sens_arr[6],self.sens_arr[7],self.sens_arr[8]]
            DEP=self.sens_arr[9]
            DIST=self.sens_arr[10]
            InputThrust=[self.input_arr[0],self.input_arr[1],self.input_arr[2],self.input_arr[3]]
            InputServo=[self.input_arr[4],self.input_arr[5]]
            SendData=[*ACC,*GYR,*EUL,DIST,DEP,
                    *InputThrust,
                    *InputServo,
                    *EncodeStatus]
        print(SendData)
        
            
        
        # データのバイナリ化
        SendDataBin=pickle.dumps(SendData)
        # データの送信
        self.ComAgent.sendto(SendDataBin,(self.PC_IP,COMMON.PCPort))
        

        # # # データ受信
        try:
            RecvData,Fromaddr=self.ComAgent.recvfrom(1024)
            self.data_separater(pickle.loads(RecvData))
            self.set_status("STSOCKET","WORKING")


        except socket.timeout:
            self.set_status("STSOCKET","TIMEOUT")
            # print("timeout")



# ---I2Cモジュール管理---
@ray.remote(num_cpus=1)
class I2CManager:
    def __init__(self,IFManager,sens_memory_name,input_memory_name,status_memory_name):
        import smbus

        # ステータスのデコーダを準備する。
        self.SA=COMMON.StatusAnalyzer()

        # i2cモジュール立ち上げ
        self.i2c=smbus.SMBus(1)
        
        # タスク回転フラグ
        self.task_run=True

        #モジュール使用不使用選択
        self.IMU_ENABLE=True
        self.DEPTH_ENABLE=False
        self.DIST_ENABLE=False
        self.THRUST_ENABLE=False
        self.SERVO_ENABLE=False
        self.CHUSYAKI_ENABLE=False

        # 共有メモリ
        # センサメモリ
        self.sens_memory=shared_memory.SharedMemory(name=sens_memory_name)
        self.sens_arr=np.ndarray((11,),dtype=np.float32,buffer=self.sens_memory.buf)
        # 入力メモリ
        self.input_memory=shared_memory.SharedMemory(name=input_memory_name)
        self.input_arr=np.ndarray((8,),dtype=np.float32,buffer=self.input_memory.buf)
        # ステータスメモリ
        self.status_memory=shared_memory.SharedMemory(name=status_memory_name)
        self.status_arr=np.ndarray((7,),dtype=np.int8,buffer=self.status_memory.buf)


        # ステータスマネージャー
        self.IFManager=IFManager

        
        while True:
            STSOCKET=self.SA.Decoder(self.status_arr)[0]
            time.sleep(1)
            print(STSOCKET)
            if STSOCKET=="WORKING":
                break
            
        threading.Thread(target=self.main_task,daemon=True).start()
    
    def InitModules(self):


        if self.IMU_ENABLE:
            self.IMU=ICM20948(self.i2c,DEBUG_PRINT)
        if self.DEPTH_ENABLE:
            self.DS = ms5837.MS5837_02BA(self.i2c)
        if self.DIST_ENABLE:
            self.SS=sen0599.sen0599() 
        if self.THRUST_ENABLE:
            self.TH=THRUSTER(self.i2c,0,1,2,3,DEBUG_PRINT)
        if self.SERVO_ENABLE:
            self.SRV=SERVO(self.i2c,4,5,DEBUG_PRINT)
        if self.CHUSYAKI_ENABLE:
            self.CHU1=TB6612(self.i2c,PCA9685,7,20,21,DEBUG_PRINT,LimitEnable=False)
            self.CHU2=TB6612(self.i2c,PCA9685,6,12,16,DEBUG_PRINT,LimitEnable=False)
    
    def ModuleCalibration(self):
        

        if self.DEPTH_ENABLE:
            self.DepthCalibration()
            time.sleep(0.5)

        if self.DIST_ENABLE:
            self.DistCalibration()
            time.sleep(0.5)

        if self.IMU_ENABLE:
            self.IMUCalibration()
            time.sleep(0.5)
        else:
            self.IFManager.set_status.remote("STIMU","READY")
            time.sleep(0.5)

        if self.THRUST_ENABLE:
            self.ThrustCalibration()
            time.sleep(0.5)
        else:
            self.IFManager.set_status.remote("STTHRUST","READY")
            time.sleep(0.5)

        if self.SERVO_ENABLE:
            self.ServoCalibration()
            time.sleep(0.5)
        else :
            self.IFManager.set_status.remote("STSERVO","READY")
            time.sleep(0.5)
        
        if self.CHUSYAKI_ENABLE:
            self.ChusyakiCalibration()
            time.sleep(0.5)
        else:
            self.IFManager.set_status.remote("STCHU","READY")
            time.sleep(0.5)
        
        self.IFManager.set_status.remote("STCAMERA","READY")


    
    def IMUCalibration(self):
        # IMU
        self.IMU.hello()
        self.IMU.setup()
        # センサ設定
        self.IMU.set_scale_gyr("500dps")
        self.IMU.set_scale_acc("2G")
        self.IFManager.set_status.remote("STIMU","SETUP")
        # キャリブレーション
        self.IFManager.set_status.remote("STIMU","CALIBRATION")
        self.IFManager.set_status.remote("STIMU",self.IMU.calibration(1000))
        # 姿勢角推定設定
        self.EST=MadgwickAHRS(sampleperiod=0.01,beta=1.0)
        self.IFManager.set_status.remote("STIMU","READY")

    
    def DepthCalibration(self):
        self.DS.init()
        self.DS.read(ms5837.OSR_256)
        self.DS.setFluidDensity(ms5837.DENSITY_FRESHWATER)
    
    def DistCalibration(self):
        self.SS=sen0599.sen0599()
    
    def ThrustCalibration(self):
        # キャリブレーション
        self.IFManager.set_status.remote("STTHRUST","CALIBRATION")
        self.IFManager.set_status.remote("STTHRUST",self.TH.Calibration())
        self.TH.set_thrust(1650,1650,1650,1650)
        self.IFManager.set_status.remote("STTHRUST","READY")

    def ServoCalibration(self):
        # キャリブレーション（と言ってるが動かしてるだけ）
        self.IFManager.set_status.remote("STSERVO","CALIBRATION")
        time.sleep(0.1)
        self.IFManager.set_status.remote("STSERVO",self.SRV.Caribration())
        self.IFManager.set_status.remote("STSERVO","READY")
        
    def ChusyakiCalibration(self):
        # キャリブレーション(と言ってるが動かしてるだけ)
        self.IFManager.set_status.remote("STCHU","CALIBRATION")
        if self.CHU1.caribration()=="CALIBRATION_OK" and self.CHU2.caribration()=="CALIBRATION_OK":
            self.IFManager.set_status.remote("STCHU","CALIBRATION_OK")
        self.IFManager.set_status.remote("STCHU","READY")
        time.sleep(2)
    
    def main_task(self):
        self.InitModules()
        self.ModuleCalibration()

        while self.task_run:
            # IMUデータ取得

            if self.IMU_ENABLE:
                gyr=self.IMU.get_gyr()
                acc=self.IMU.get_acc()
                self.EST.update_imu(gyr,acc)
                eul=self.EST.quaternion.to_euler_angles_ZYX()
            else :
                gyr=[0.0,0.0,0.0]
                acc=[0.0,0.0,0.0]
                eul=[0.0,0.0,0.0]
            
            # 深度センサ
            if self.DEPTH_ENABLE:
                self.DS.read(ms5837.OSR_256)
                dep=self.DS.depth()
            else :
                dep=0
            
            # 超音波センサ
            if self.DIST_ENABLE:
                dist=self.SS.read_data()
            else:
                dist=0
            
            # 共有メモリへ書き込み
            self.sens_arr[:]=[gyr[0],gyr[1],gyr[2],
                              acc[0],acc[1],acc[2],
                              eul[0],eul[1],eul[2],
                              float(dep),float(dist)]
            
            InputData=self.input_arr

            # モジュール操作入力
            if self.THRUST_ENABLE:
                self.TH.set_thrust(InputData[0],InputData[1],InputData[2],InputData[3])
            if self.SERVO_ENABLE:
                self.SRV.set_servo(InputData[4],InputData[5])
            if self.CHUSYAKI_ENABLE:
                self.CHU1.set_chusyaki(InputData[6])
                self.CHU2.set_chusyaki(InputData[7])
            
            time.sleep(1)

    def stop_task(self):
        self.task_run=False


# ---コントローラ---
@ray.remote(num_cpus=1)
class Control:
    def __init__(self,IFManager,sens_memory_name,input_memory_name,propo_memory_name,gain_memory_name,status_memory_name):
        # タスク回転フラグ
        self.task_run=True

        # IFマネージャー
        self.IFManager=IFManager

        # 共有メモリ
        # センサメモリ
        self.sens_memory=shared_memory.SharedMemory(name=sens_memory_name)
        self.sens_arr=np.ndarray((11,),dtype=np.float32,buffer=self.sens_memory.buf)
        # 入力値メモリ
        self.input_memory=shared_memory.SharedMemory(name=input_memory_name)
        self.input_arr=np.ndarray((8,),dtype=np.float32,buffer=self.input_memory.buf)
        # プロポメモリ
        self.propo_memory=shared_memory.SharedMemory(name=propo_memory_name)
        self.propo_arr=np.ndarray((11,),dtype=np.float32,buffer=self.propo_memory.buf)
        # ゲインメモリ
        self.gain_memory=shared_memory.SharedMemory(name=gain_memory_name)
        self.gain_arr=np.ndarray((9,),dtype=np.float32,buffer=self.gain_memory.buf)
        # ステータスメモリ
        self.status_memory=shared_memory.SharedMemory(name=status_memory_name)
        self.status_arr=np.ndarray((7,),dtype=np.int8,buffer=self.status_memory.buf)

        self.Con=Controller()

        threading.Thread(target=self.TimerFunc,daemon=True).start()
        
    
    def TimerFunc(self):
        COMMON.scheduler(0.01,lambda: self.main_task(),enable=self.task_run)
    
    def stop_task(self):
        self.task_run=False
    
    def main_task(self):
        STCONTROLLER=self.IFManager.get_status.remote("STCONTROLLER")
        # InputData=self.Con.Controller(self.propo_arr,self.sens_arr,self.gain_arr,STCONTROLLER)
        # self.input_arr[:]=[InputData[0],InputData[1],InputData[2],InputData[3],InputData[4],InputData[5],InputData[6],InputData[7]]
        
        



# 共有メモリをopen
# センサデータ
sens_memory=shared_memory.SharedMemory(create=True, size=np.zeros(11, dtype=np.float32).nbytes)
sens_arr = np.ndarray((11,), dtype=np.float32, buffer=sens_memory.buf)
# 入力データ
input_memory=shared_memory.SharedMemory(create=True, size=np.zeros(8, dtype=np.float32).nbytes)
input_arr = np.ndarray((8,), dtype=np.float32, buffer=input_memory.buf)
# プロポデータ
propo_memory=shared_memory.SharedMemory(create=True, size=np.zeros(11, dtype=np.float32).nbytes)
propo_arr=np.ndarray((11,), dtype=np.float32, buffer=propo_memory.buf)
# PIDゲイン
gain_memory=shared_memory.SharedMemory(create=True, size=np.zeros(9, dtype=np.float32).nbytes)
gain_arr=np.ndarray((9,), dtype=np.float32, buffer=gain_memory.buf)
# ステータスでーた
status_memory=shared_memory.SharedMemory(create=True, size=np.zeros(7, dtype=np.int8).nbytes)
status_arr=np.ndarray((7,), dtype=np.int8, buffer=status_memory.buf)

IF=IFManager.remote(sens_memory.name,input_memory.name,propo_memory.name,gain_memory.name,status_memory.name)
I2C=I2CManager.remote(IF,sens_memory.name,input_memory.name,status_memory.name)
# MotionControl=Control.remote(IF,sens_memory.name,input_memory.name,propo_memory.name,gain_memory.name,status_memory.name)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    ray.get(IF.stop_task.remote())
    ray.get(I2C.stop_task.remote())
    # ray.get(MotionControl.stop_task.remote())

    sens_memory.close()
    sens_memory.unlink()
    input_memory.close()
    input_memory.unlink()
    propo_memory.close()
    propo_memory.unlink()
    gain_memory.close()
    gain_memory.unlink()

    ray.shutdown
    SystemCheck.wifi_on()