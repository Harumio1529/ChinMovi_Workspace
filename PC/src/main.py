import sys
import os

# ライブラリインポート
import socket,time,pickle,math
from multiprocessing import Process,Array,Value,Lock

# 自作ライブラリ
from lib.propo.Propo import ps4
import gui



# 通信用顧問
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import COMMON
SA=COMMON.StatusAnalyzer()

# デバッグモード
DEBUG_MODE=False





# データコンテナ
acc=Array("d",3)
gyr=Array("d",3)
eul=Array("d",3)
STSOCKET=Value("i",0)
STIMU=Value("i",0)
STTHRUST=Value("i",0)
STSERVO=Value("i",0)
STCHU=Value("i",0)
STCAMERA=Value("i",0)
STCONTROLLER=Value("i",0)

#コントローラー初期化
stknum=6
btnnum=16
propo=ps4(stknum,btnnum)
PropoData=Array("d",(stknum+btnnum))

def data_input(container,data,lock):
    with lock:
        for i in range(data):
            container[i]=data[i]


def data_separeter(data,acc,gyr,eul,STSOCKET,STIMU,STTHRUST,STSERVO,STCHU,STCAMERA,STCONTROLLER):
        data_input(acc,data[0:3],Lock)
        data_input(gyr,data[3:6],Lock)
        data_input(eul,data[6:9],Lock)
        with Lock:
            STSOCKET.value=data[9]
            STIMU.value=data[10]
            STTHRUST.value=data[11]
            STSERVO.value=data[12]
            STCHU.value=data[13]
            STCAMERA.value=data[14]
            STCONTROLLER.value-data[15]

def status_controler(STSOCKET,STIMU,STTHRUST,STSERVO,STCHU,STCAMERA,STCONTROLLER):
    with Lock:
    # ステータスを監視して、全部ReadyならWorkingに遷移してもらう
        if STIMU.value=="READY" and STTHRUST.value=="READY" and STSERVO.value=="READY" and STCHU.value=="READY" and STCAMERA.value=="READY":
            STIMU.value="WORKING"
            STTHRUST.value="WORKING"
            STSERVO.value="WORKING"
            STCHU.value="WORKING"
            STCAMERA.value="SERCH_MODE"
            STCONTROLLER.value="MANUAL_CONTROL"
        # ステータスのエンコード
        return SA.Encoder([STSOCKET.value,STIMU.value,STTHRUST.value,STSERVO.value,STCHU.value,STCAMERA.value,STCONTROLLER.value])

    
def Com_Process(acc,gyr,eul,STSOCKET,STIMU,STTHRUST,STSERVO,STCHU,STCAMERA,STCONTROLLER):
    # 通信チェック
    # デバッグモードなら通信チェックなし
    if DEBUG_MODE:
        RasPi_IP="0.0.0.0"
        PC_IP="0.0.0.0"
    else:    
        RasPi_IP,PC_IP=COMMON.CheckIPAddress("PC")
        
    # UDP通信クライアント設立
    ComAgent=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    ComAgent.bind((PC_IP,COMMON.PCPort))
    ComAgent.settimeout(1)
    COMMON.scheduler(0.01,lambda:Com_Process_main(ComAgent,RasPi_IP,acc,gyr,eul,STSOCKET,STIMU,STTHRUST,STSERVO,STCHU,STCAMERA,STCONTROLLER))


def Com_Process_main(ComAgent,RasPi_IP,acc,gyr,eul,STSOCKET,STIMU,STTHRUST,STSERVO,STCHU,STCAMERA,STCONTROLLER):
    try:
        # データ受信
        data,addr=ComAgent.recvfrom(1024)
        # 受信データ分割
        data_separeter(pickle.loads(data),acc,gyr,eul,STSOCKET,STIMU,STTHRUST,STSERVO,STCHU,STCAMERA,STCONTROLLER)
        # ステータス監視
        EncodeStatus=status_controler(STSOCKET,STIMU,STTHRUST,STSERVO,STCHU,STCAMERA,STCONTROLLER)
        # プロポデータ取得
        PropoData.put(propo.getPropoData())
        # 送信データ作成
        SendData=[*PropoData.peek(),*EncodeStatus]
        ComAgent.sendto(pickle.dumps(SendData),(RasPi_IP,COMMON.RasPiPort))
        # print(acc.get_emptychck())
        # print(pickle.loads(data))
        # print([STSOCKET.peek(),STIMU.peek(),STTHRUST.peek(),STSERVO.peek(),STCHU.peek(),STCAMERA.peek(),STCONTROLLER.peek()])
    
    except socket.timeout:
        print("timeout")
        pass



def function(lock):
    with lock:
        return list(acc)


if __name__=="__main__":
    CP=Process(target=Com_Process,
               args=(
                   acc,gyr,eul,
                   STSOCKET,STIMU,STTHRUST,STSERVO,STCHU,STCAMERA,STCONTROLLER))
    CP.daemon=True
    CP.start()
    gui.gui_start(function)
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("fin")
    








        




