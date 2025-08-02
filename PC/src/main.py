import sys
import os

# ライブラリインポート
import socket,time,pickle,math
import threading

# 自作ライブラリ
from lib.propo.Propo import ps4
import gui
from lib.CustomQueue.customqueue import CustomQueue_withThred



# 通信用顧問
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import COMMON
SA=COMMON.StatusAnalyzer()

# デバッグモード
DEBUG_MODE=False





# データコンテナ
acc=CustomQueue_withThred(init_item=([0]*3),maxsize=10)
gyr=CustomQueue_withThred(init_item=([0]*3),maxsize=10)
eul=CustomQueue_withThred(init_item=([0]*3),maxsize=10)
dist=CustomQueue_withThred(init_item=0,maxsize=10)
dep=CustomQueue_withThred(init_item=0,maxsize=10)
InputThrsut=CustomQueue_withThred(init_item=([0]*4),maxsize=10)
InputServo=CustomQueue_withThred(init_item=([0]*2),maxsize=10)
STSOCKET=CustomQueue_withThred(init_item="",maxsize=10)
STIMU=CustomQueue_withThred(init_item="",maxsize=10)
STTHRUST=CustomQueue_withThred(init_item="",maxsize=10)
STSERVO=CustomQueue_withThred(init_item="",maxsize=10)
STCHU=CustomQueue_withThred(init_item="",maxsize=10)
STCAMERA=CustomQueue_withThred(init_item="",maxsize=10)
STCONTROLLER=CustomQueue_withThred(init_item="",maxsize=10)

#コントローラー初期化
stknum=6
btnnum=16
propo=ps4(stknum,btnnum)
PropoData=CustomQueue_withThred(init_item=[0]*(stknum+btnnum),maxsize=10)


def data_separeter(data):
        # IMUData[0~8] 9
        gyr.put(data[0:3])
        acc.put(data[3:6])
        eul.put(data[6:9])
        # SSData[9] 1
        dist.put(data[9])
        # DepthData[10] 1
        dep.put(data[10])
        # ThsrutinputData[11~14]4
        InputThrsut.put(data[11:15])
        # ServoinputData[15~16] 2
        InputServo.put(data[15:17])
        # Statusdata[17~fin]
        StatusData=SA.Decoder(data[17:])
        STSOCKET.put(StatusData[0])
        STIMU.put(StatusData[1])
        STTHRUST.put(StatusData[2])
        STSERVO.put(StatusData[3])
        STCHU.put(StatusData[4])
        STCAMERA.put(StatusData[5])
        STCONTROLLER.put(StatusData[6])

def status_controler():
    # ステータスを監視して、全部ReadyならWorkingに遷移してもらう
    if STIMU.get_emptychck()=="READY" and STTHRUST.get_emptychck()=="READY" and STSERVO.get_emptychck()=="READY" and STCHU.get_emptychck()=="READY" and STCAMERA.get_emptychck()=="READY":
        STIMU.put("WORKING")
        STTHRUST.put("WORKING")
        STSERVO.put("WORKING")
        STCHU.put("WORKING")
        STCAMERA.put("VIDEO_MODE")
        STCONTROLLER.put("MANUAL_CONTROL")
    # ステータスがすべてworkingの場合にGUIからの変更を受け付ける
    if STIMU.get_emptychck()=="WORKING" and STTHRUST.get_emptychck()=="WORKING" and STSERVO.get_emptychck()=="WORKING" and STCHU.get_emptychck()=="WORKING":
        SelectedCameraMode,SelectedControlMode=gui.GetControlModeDatafromGUI()
        STCAMERA.put(SelectedCameraMode)
        STCONTROLLER.put(SelectedControlMode)

    # ステータスのエンコード
    return SA.Encoder([STSOCKET.get_emptychck(),STIMU.get_emptychck(),STTHRUST.get_emptychck(),STSERVO.get_emptychck(),STCHU.get_emptychck(),STCAMERA.get_emptychck(),STCONTROLLER.get_emptychck()])

    
def Com_Thred():
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
    COMMON.scheduler(0.01,lambda:Com_Thred_main(ComAgent,RasPi_IP))


def Com_Thred_main(ComAgent,RasPi_IP):
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
        SendData=[*PropoData.peek(),*gui.GetPIDGainfromGUI(),*EncodeStatus]
        ComAgent.sendto(pickle.dumps(SendData),(RasPi_IP,COMMON.RasPiPort))
    
    except socket.timeout:
        # print("timeout")
        pass



def function():
    return [STSOCKET,STIMU,STTHRUST,STSERVO,STCHU,STCAMERA,STCONTROLLER],[acc.get_emptychck(),gyr.get_emptychck(),eul.get_emptychck(),dist.get_emptychck(),dep.get_emptychck()],PropoData.get_emptychck(),InputThrsut.get_emptychck(),InputServo.get_emptychck()



if __name__=="__main__":
    threading.Thread(target=Com_Thred,daemon=True).start()
    gui.gui_start(function)
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("fin")
    








        




