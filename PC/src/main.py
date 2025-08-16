import sys
import os

# ライブラリインポート
import socket,time,pickle,math
import threading
from datetime import datetime

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

# ログヘッダ用
LogHead=True

# ファイル名前
# logpath='C:\work\ChinMovi_Workspace\PC\log' #ノート
logpath="C:\work\ChinMovi_Workspace\PC\log"#desktop
now=datetime.now().strftime("%Y-%m-%d_%H_%M_%S")
logfilename=logpath+"\LogData_"+now+".csv"







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

iter=0
data=[0]*(stknum+btnnum)
y_=0
f=0.005

def InputNormarize(input):
    return (input-1600)/600

def GenLogData(data):
    AccData=str(data[0])+","+str(data[1])+","+str(data[2])
    GyrData=str(data[3])+","+str(data[4])+","+str(data[5])
    EulData=str(data[6])+","+str(data[7])+","+str(data[8])
    DistData=str(data[9])
    DepData=str(data[10])
    InputData=str(InputNormarize(data[11]))+","+str(InputNormarize(data[12]))+","+str(InputNormarize(data[13]))+","+str(InputNormarize(data[14]))
    PD=PropoData.get_emptychck()
    surge=-0.5*(PD[4]+1)+0.5*(PD[5]+1)
    TargetData=str(-1*PD[1])+","+str(PD[2])+","+str(-1*PD[3])+","+str(surge)
    ControlModeData=str(data[23])

    return AccData+","+GyrData+","+EulData+","+DistData+","+DepData+","+InputData+","+TargetData+","+ControlModeData


def data_separeter(data):
    # IMUData[0~8] 9
    acc.put(data[0:3])
    gyr.put(data[3:6])
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

    
    start_time = start_time0
    start_time = time.perf_counter()
    if data[23]>0.5:
        #logを書く
        timestamp = str(start_time-start_time0).split('.')
        timestamp_ = timestamp[0] + '.' + timestamp[1][:3]
        log_string = f'{timestamp_},' +GenLogData(data)
        outputFile.write(log_string+"\n")


    

def status_controler():
    print([STSOCKET.get_emptychck(),STIMU.get_emptychck(),STTHRUST.get_emptychck(),STSERVO.get_emptychck(),STCHU.get_emptychck(),STCAMERA.get_emptychck(),STCONTROLLER.get_emptychck()])
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

def GenSystemIdentData(f0,f1,maxiter,amp):
    global iter,data,y_,f
    freq=f0+(f1-f0)*(iter/maxiter)
    phase=2*math.pi*freq*iter
    # phase = iter*f
    y=amp*math.sin(phase)
    # if y_<=0 and y>=0:
    #     f*=1.2

    print(data[1])

    
    data[0]=0
    data[1]=y
    data[2]=0
    data[3]=0
    data[4]=0
    data[5]=0
    data[6]=0
    data[7]=0
    data[8]=0
    data[9]=0
    data[10]=0
    data[11]=0
    data[12]=0
    data[13]=0
    data[14]=0
    data[15]=0
    data[16]=0
    data[17]=0
    data[18]=0
    data[19]=0
    data[20]=0
    data[21]=0

    if iter<=maxiter:
        iter+=0.01
    else :
        y=0
    y_=y

    return data
    




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
        if EncodeStatus[6]==3:
            PropoData.put(GenSystemIdentData(0.2,5,30,0.8))
        # 送信データ作成
        SendData=[*PropoData.peek(),*gui.GetPIDGainfromGUI(),*EncodeStatus]
        ComAgent.sendto(pickle.dumps(SendData),(RasPi_IP,COMMON.RasPiPort))
    
    except socket.timeout:
        # print("timeout")
        pass



def function():
    return [STSOCKET,STIMU,STTHRUST,STSERVO,STCHU,STCAMERA,STCONTROLLER],[acc.get_emptychck(),gyr.get_emptychck(),eul.get_emptychck(),dist.get_emptychck(),dep.get_emptychck()],PropoData.get_emptychck(),InputThrsut.get_emptychck(),InputServo.get_emptychck()




if __name__=="__main__":
    with open(logfilename,"w") as outputFile:
        outputFile.write("t,ax,ay,az,gx,gy,gz,roll,pitch,heading,dist,depth,u1,u2,u3,u4,Heave,Yawing,Pitching,Surge,ControlMode\n")
        # ログデータ取得
        start_time0 = time.perf_counter()
        threading.Thread(target=Com_Thred,daemon=True).start()
        gui.gui_start(function)
        try:
            while True:
                pass
        except KeyboardInterrupt:
            print("fin")
    








        




