import sys
import os

# ライブラリインポート
import socket,time,pickle,math
# GUI関連
from PyQt6.QtWidgets import QApplication
import pyqtgraph as pg
from PyQt6.QtWidgets import QMainWindow,QApplication
from PyQt6 import uic
from PyQt6.QtCore import QTimer

# 自作ライブラリ
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))
from lib.propo.Propo import ps4
from lib.gui.plot import mainwindow

# 通信用顧問
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../..")))
import COMMON
SA=COMMON.StatusAnalyzer()

# デバッグモード
DEBUG_MODE=False

# 通信チェック
# デバッグモードなら通信チェックなし
if DEBUG_MODE:
    RasPi_IP="0.0.0.0"
    PC_IP="0.0.0.0"
else:    
    RasPi_IP,PC_IP=COMMON.CheckIPAddress("PC")


# 受信データコンテナ
acc=[0]*3
gyr=[0]*3
eul=[0]*3
STSOCKET=""
STIMU=""
STTHRUST=""
STSERVO=""
STCHU=""

#コントローラー初期化
stknum=6
btnnum=16
propo=ps4(stknum,btnnum)
PropoData=[0]*(stknum+btnnum)

# UDP通信クライアント設立
ComAgent=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
ComAgent.bind((PC_IP,COMMON.PCPort))
ComAgent.settimeout(1)

def data_separeter(data):
    global acc,gyr,eul,STSOCKET,STIMU,STTHRUST,STSERVO,STCHU
    acc=data[0:3]
    gyr=data[3:6]
    eul=data[6:9]
    [STSOCKET,STIMU,STTHRUST,STSERVO,STCHU]=SA.Decoder(data[9:])

def status_controler():
    global STSOCKET,STIMU,STTHRUST,STSERVO,STCHU
    # ステータスを監視して、全部ReadyならWorkingに遷移してもらう
    if STIMU=="READY" and STTHRUST=="READY" and STSERVO=="READY" and STCHU=="READY":
        STIMU="WORKING"
        STTHRUST="WORKING"
        STSERVO="WORKING"
        STCHU="WORKING"
    # ステータスのエンコード
    return SA.Encoder([STSOCKET,STIMU,STTHRUST,STSERVO,STCHU])

    
    

def Com_main():
    global PropoData
    try:
        # データ受信
        data,addr=ComAgent.recvfrom(1024)
        # 受信データ分割
        data_separeter(pickle.loads(data))
        # ステータス監視
        EncodeStatus=status_controler()
        # プロポデータ取得
        PropoData=propo.getPropoData()
        # print(PropoData)
        # 送信データ作成
        SendData=[*PropoData,*EncodeStatus]
        ComAgent.sendto(pickle.dumps(SendData),(RasPi_IP,COMMON.RasPiPort))
        # print(pickle.loads(data))
        print([STSOCKET,STIMU,STTHRUST,STSERVO,STCHU])
    
    except socket.timeout:
        print("timeout")
        pass



COMMON.scheduler(0.01,Com_main)
        




