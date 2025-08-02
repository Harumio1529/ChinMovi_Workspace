# 標準ライブラリをimport
import sys ,os
import socket,time,pickle,smbus,threading,queue,cv2
from multiprocessing import Process

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
Con=Controller()

SystemCheck.wifi_off()



### デバッグモード ###
DEBUG_MODE=False
DEBUG_PRINT=True
#モジュール使用不使用選択
THRUST_ENABLE=True
SERVO_ENABLE=True
CHUSYAKI_ENABLE=True
CAMERA_ENABLE=False


#デバッグ用コンソール出力
def debugprint(data):
    if DEBUG_PRINT:
        print(data)

# Queueデータの箱を準備する
SensorData=CustomQueue_withThred(init_item=([[0]*3,[0]*3,[0]*3,[0],[0]]),maxsize=10)
PropoData=CustomQueue_withThred(init_item=([0]*10),maxsize=10)
InputThrust=CustomQueue_withThred(init_item=([0]*4),maxsize=10)
InputServo=CustomQueue_withThred(init_item=([0]*2),maxsize=10)
PIDGain=CustomQueue_withThred(init_item=([0]*9),maxsize=10)
STSOCKET=CustomQueue_withThred(init_item="PREPARING",maxsize=10)
STIMU=CustomQueue_withThred(init_item="PREPARING",maxsize=10)
STTHRUST=CustomQueue_withThred(init_item="PREPARING",maxsize=10)
STSERVO=CustomQueue_withThred(init_item="PREPARING",maxsize=10)
STCHU=CustomQueue_withThred(init_item="PREPARING",maxsize=10)
STCAMERA=CustomQueue_withThred(init_item="PREPARING",maxsize=10)
STCONTROLLER=CustomQueue_withThred(init_item="PREPARING",maxsize=10)


#### 通信スレッド用関数 ####
def Com_Thred(ComAgent: socket.socket):
    COMMON.scheduler(0.01,lambda: Com_Thred_main(ComAgent))

# プロポのデータを選別する。22→10
def data_selector(data):
    # 使用データは設計書参照
    return [data[0],data[1],
            data[4],data[5],
            data[15],data[16],
            data[17],data[18],data[19],data[20]]
    
# 通信データをステータスとプロポのデータに分ける
def data_separater(data):
    # 前から22個はプロポのデータが入ってくる
    PropoData.put(data_selector(data[:22]))
    # そのあと9個はPIDゲインが入ってくる
    PIDGain.put(data[22:31])
    # それより後ろはステータスのデータ
    StatusData=SA.Decoder(data[31:])
    if StatusData[0]=="WORKING":
        STSOCKET.put(StatusData[0])
    if StatusData[1]=="WORKING":
        STIMU.put(StatusData[1])
    if StatusData[2]=="WORKING":
        STTHRUST.put(StatusData[2])
    if StatusData[3]=="WORKING":
        STSERVO.put(StatusData[3])
    if StatusData[4]=="WORKING":
        STCHU.put(StatusData[4])
    if StatusData[5]=="SERCH_MODE" or StatusData[5]=="VIDEO_MODE":
        STCAMERA.put(StatusData[5])
    if StatusData[6]!="PREPARING":
        STCONTROLLER.put(StatusData[6])
    
    
    # print([STSOCKET.peek(),STIMU.peek(),STTHRUST.peek(),STSERVO.peek(),STCHU.peek(),STCAMERA.peek(),STCONTROLLER.peek(),
    #        *PropoData.peek()])

    

# 通信スレッド用main関数
def Com_Thred_main(ComAgent: socket.socket):
    # 送信用データまとめ
    # 送信用データの中身([byte])
    # [ACC_X(4),ACC_Y(4),ACC_Z(4),GYR_X(4),GYR_Y(4),GYR_Z(4),PITCH(4),ROLL(4),YAW(4),STSOCKET(1),STIMU(1),STTHRUST(1),STSERVO(1),STCHU(1),STCAMERA(1)]
    # ステータス信号のエンコード
    EncodeStatus=SA.Encoder([STSOCKET.get_emptychck(),
                             STIMU.get_emptychck(),
                             STTHRUST.get_emptychck(),
                             STSERVO.get_emptychck(),
                             STCHU.get_emptychck(),
                             STCAMERA.get_emptychck(),
                             STCONTROLLER.get_emptychck()])

    # print(EncodeStatus)
    # センサデータをぶち込む
    if STIMU.get_emptychck()!="WORKING" and STTHRUST.get_emptychck()!="WORKING":
        SendData=[0.0,0.0,0.0,      #加速度
                  0.0,0.0,0.0,      #ジャイロ
                  0.0,0.0,0.0,      #オイラー各
                  0.0,              #超音波センサ
                  0.0,              #深度センサ
                  0.0,0.0,0.0,0.0,  #スラスタ指示値
                  0.0,0.0,          #サーボ指示値
                  *EncodeStatus]
    else :
        SendData=[*SensorData.get_emptychck(),*InputThrust.get_emptychck(),*InputServo.get_emptychck(),*EncodeStatus]
        
    
    # データのバイナリ化
    SendDataBin=pickle.dumps(SendData)
    # データの送信
    ComAgent.sendto(SendDataBin,(PC_IP,COMMON.PCPort))
    

    # # # データ受信
    try:
        RecvData,Fromaddr=ComAgent.recvfrom(1024)
        data_separater(pickle.loads(RecvData))
        STSOCKET.put("WORKING")

    except socket.timeout:
        STSOCKET.put("TIMEOUT")
        # print("timeout")


# メインスレッドの実行関数 #
def Module_Thred_main(TH,SRV,CHU1,CHU2):
    # センサデータ取得
    gyr=IMU.get_gyr()
    acc=IMU.get_acc()
    EST.update_imu(gyr,acc)
    eul=EST.quaternion.to_euler_angles_ZYX()
    dist=SS.read_data()
    dep=DS.depth()
    SensorData.put([gyr,acc,eul,dist,dep])
    # 入力値計算
    InputData=Con.Controller(PropoData.get_emptychck(),
                    SensorData.get_emptychck(),
                    PIDGain.get_emptychck(),
                    STCONTROLLER.get_emptychck())
    # モジュール工藤
    TH.set_thrust(InputData[0][0],InputData[0][1],InputData[0][2],InputData[0][3])
    SRV.set_servo(InputData[1][0],InputData[1][1])
    CHU1.set_chusyaki(InputData[2][0])
    CHU2.set_chusyaki(InputData[2][1])
    # GUI送信用
    InputThrust.put(InputData[0])
    InputServo.put(InputData[1])
    


### カメラ処理用スレッド（別コアで駆動） ###
def Camera_Process_main():
    while True:
        if STCAMERA=="SERCH_MODE":
            ret, low = cap.read()
            frame=CM.Clahe(low)
            
        else :
            ret, frame = cap.read()
            frame=CM.Clahe(frame)
        
        cv2.imshow('image', frame)
        key = cv2.waitKey(1)
        if key == ord('q'):  # qキーで終了
            break

    cap.release()
    cv2.destroyAllWindows()











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
debugprint(STSOCKET.empty())
STSOCKET.put("COM_OK")

# COMエージェント立ち上げ
STSOCKET.put("STANDUP_COMAGENT")
ComAgent=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ComAgent.settimeout(0.05)
ComAgent.bind((RasPI_IP, COMMON.RasPiPort))
STSOCKET.put("READY")
debugprint("socket com is READY!")

threading.Thread(target=Com_Thred,args=(ComAgent,),daemon=True).start()

# センサモジュール起動
IMU=ICM20948(i2c,DEBUG_PRINT)
IMU.hello()
IMU.setup()
# センサ設定
IMU.set_scale_gyr("500dps")
IMU.set_scale_acc("2G")
STIMU.put("SETUP")
# キャリブレーション
STIMU.put("CALIBRATION")
STIMU.put(IMU.calibration(1000))
# 姿勢角推定
EST=MadgwickAHRS(sampleperiod=0.01,beta=1.0)
# 深度センサ
DS = ms5837.MS5837_30BA(i2c)
DS.init()
DS.read(ms5837.OSR_256)
DS.setFluidDensity(ms5837.DENSITY_FRESHWATER)
debugprint("Depth OK!")
#超音波センサ
SS=sen0599.sen0599() 
debugprint("SS OK!")

STIMU.put("READY")
debugprint("IMU and Estimation is READY !")

if THRUST_ENABLE:
    # スラスタモジュール起動
    TH=THRUSTER(i2c,0,1,2,3,DEBUG_PRINT)
    # キャリブレーション
    STTHRUST.put("CALIBRATION")
    STTHRUST.put(TH.Calibration())
    TH.set_thrust(1605,1605,1605,1605)
    time.sleep(1)
STTHRUST.put("READY")
debugprint("THRUSTER is READY !")

if SERVO_ENABLE:
    # サーボモジュール起動
    SRV=SERVO(i2c,8,9,DEBUG_PRINT)
    # キャリブレーション（と言ってるが動かしてるだけ）
    STSERVO.put("CARIBRATION")
    time.sleep(0.1)
    STSERVO.put(SRV.Caribration())
STSERVO.put("READY")
time.sleep(0.1)
debugprint("SERVO is READY !")

if CHUSYAKI_ENABLE:
    # チュウシャキモジュール起動
    CHU1=TB6612(i2c,PCA9685,7,20,21,DEBUG_PRINT,LimitEnable=False)
    CHU2=TB6612(i2c,PCA9685,6,12,16,DEBUG_PRINT,LimitEnable=False)
    # キャリブレーション(と言ってるが動かしてるだけ)
    STCHU.put("CARIBRATION")
    if CHU1.caribration()=="CARIBRATION_OK" and CHU2.caribration()=="CARIBRATION_OK":
        STCHU.put("CARIBRATION_OK")

STCHU.put("READY")
debugprint("CHUSYAKI is READY !")
time.sleep(2)

if CAMERA_ENABLE:
    # カメラモジュール起動
    cap=cv2.VideoCapture(0)
    STCAMERA.put("CAPTURE_OK")
    debugprint("Capture OK!")
    CM=camera(DEBUG_PRINT)
    Camera_Process=Process(target=Camera_Process_main)
    Camera_Process.daemon=True
    Camera_Process.start()
    
STCAMERA.put("READY")





try:
    # 100Hzで実行
    COMMON.scheduler(0.01,lambda:Module_Thred_main(TH,SRV,CHU1,CHU2))
except KeyboardInterrupt:
    TH.close()
    SRV.close()
    CHU1.close()
    CHU2.close()
    SystemCheck.wifi_on()

