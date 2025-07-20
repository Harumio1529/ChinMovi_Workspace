import sys
import os

# ライブラリインポート
import socket,time,pickle,math
from multiprocessing import Process

# 自作ライブラリ
from lib.propo.Propo import ps4
from lib.CustomQueue.customqueue import CustomQueue
import gui



# 通信用顧問
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import COMMON
SA=COMMON.StatusAnalyzer()

# デバッグモード
DEBUG_MODE=False





# データコンテナ
acc=CustomQueue(init_item=([0]*3),maxsize=10)
gyr=CustomQueue(init_item=([0]*3),maxsize=10)
eul=CustomQueue(init_item=([0]*3),maxsize=10)
STSOCKET=CustomQueue(init_item="",maxsize=10)
STIMU=CustomQueue(init_item="",maxsize=10)
STTHRUST=CustomQueue(init_item="",maxsize=10)
STSERVO=CustomQueue(init_item="",maxsize=10)
STCHU=CustomQueue(init_item="",maxsize=10)
STCAMERA=CustomQueue(init_item="",maxsize=10)
STCONTROLLER=CustomQueue(init_item="",maxsize=10)

#コントローラー初期化
stknum=6
btnnum=16
propo=ps4(stknum,btnnum)
PropoData=CustomQueue(init_item=([0]*(stknum+btnnum)),maxsize=10)



def data_separeter(data):
    # print(data)
    acc.put(data[0:3])
    gyr.put(data[3:6])
    eul.put(data[6:9])
    StatuData=SA.Decoder(data[9:])
    STSOCKET.put(StatuData[0])
    STIMU.put(StatuData[1])
    STTHRUST.put(StatuData[2])
    STSERVO.put(StatuData[3])
    STCHU.put(StatuData[4])
    STCAMERA.put(StatuData[5])
    STCONTROLLER.put(StatuData[6])

def status_controler():
    # ステータスを監視して、全部ReadyならWorkingに遷移してもらう
    if STIMU.peek()=="READY" and STTHRUST.peek()=="READY" and STSERVO.peek()=="READY" and STCHU.peek()=="READY" and STCAMERA.peek()=="READY":
        STIMU.put("WORKING")
        STTHRUST.put("WORKING")
        STSERVO.put("WORKING")
        STCHU.put("WORKING")
        STCAMERA.put("SERCH_MODE")
        STCONTROLLER.put("MANUAL_CONTROL")
    # ステータスのエンコード
    return SA.Encoder([STSOCKET.peek(),STIMU.peek(),STTHRUST.peek(),STSERVO.peek(),STCHU.peek(),STCAMERA.peek(),STCONTROLLER.peek()])

    
def Com_Process():
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
    COMMON.scheduler(0.01,lambda:Com_Process_main(ComAgent,RasPi_IP))


def Com_Process_main(ComAgent,RasPi_IP):
    try:
        # データ受信
        data,addr=ComAgent.recvfrom(1024)
        # 受信データ分割
        data_separeter(pickle.loads(data))
        # ステータス監視
        EncodeStatus=status_controler()
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



def function():
    print(acc.get_emptychck())
    return acc.get_emptychck()


if __name__=="__main__":
    CP=Process(target=Com_Process)
    CP.daemon=True
    CP.start()
    gui.gui_start(function)
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("fin")
    








        




