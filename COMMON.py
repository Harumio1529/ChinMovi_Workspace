import socket
import time

TestPort=5000
RasPiPort=5001
PCPort=5002

KpRoll=1.0
KiRoll=2.0
KdRoll=3.0
KpPitch=4.0
KiPitch=5.0
KdPitch=6.0
KpYaw=7.0
KiYaw=8.0
KdYaw=9.0


def CheckIPAddress(module):
    if module=="PC":
        raspi_ip=socket.gethostbyname("raspberrypi.local")
        print(f"Found RaspberryPi. The IP Address is {raspi_ip} !!")
        client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client.connect((raspi_ip,TestPort))
        thisIP=client.getsockname()[0]
        print(f"This PC's IP is {thisIP} !!")
        client.close()

        # 通信チェック用のクライアント立ち上げ
        client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client.bind((thisIP,TestPort))
        client.settimeout(1)
        data=""
        while True:
            #通信確認用メッセージ送信
            msg="HelloRaspberryPi!!"
            SendData=msg.encode("utf-8")
            client.sendto(SendData,(raspi_ip,TestPort))
            print("Check Connect...")
            data,addr=client.recvfrom(1024)
            time.sleep(2)
            
            if data.decode("utf-8")=="HelloPC!!":
                # 終了処理
                client.close()
                break
        print("socket com is OK.")
        print(f"RaspberryPi's IP is {addr}")
        return addr[0],thisIP
    
    elif module=="RaspberryPi":
        client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client.bind(("",TestPort))
        client.settimeout(0.5)
        data=""

        while True:
            try:
                print("Check Connect...")
                data,addr=client.recvfrom(1024)
            
                if data.decode("utf-8")=="HelloRaspberryPi!!":
                    # 返送用メッセージ送信
                    msg="HelloPC!!"
                    SendData=msg.encode("utf-8")
                    client.sendto(SendData,addr)
                    break
            except socket.timeout:
                # print("timeout retry")
                time.sleep(2)

        thisIP=client.getsockname()[0]
        client.close()
        print("socket com is OK.")
        print(f"PC's IP is {addr}")
        return addr[0],thisIP
    
    else:
        print("The augument is invalid. Set PC or RaspberryPi")

#### 定周期大麻 ####
# interval -> 実行周期[s]
# func -> 実行関数
# def scheduler(interval, func,exectime=False):
#     base_time = time.time()
#     next_time = 0
#     while True:
#         func()
#         next_time = ((base_time - time.time()) % interval) or interval
#         time.sleep(next_time)

def scheduler(interval, func, enable=True,exectime=False):
    next_time = time.time()
    while enable:
        start = time.time()
        func()
        end = time.time()

        if exectime:
            print(f"Execution time: {end - start:.6f} sec")

        next_time += interval
        sleep_time = next_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            next_time = time.time()


        

class StatusAnalyzer:
    def __init__(self):
        self.STSOCKET_List=["PREPARING","COM_OK","STANDUP_COMAGENT","READY","WORKING","TIMEOUT"]
        self.STIMU_List=["PREPARING","SETUP","CALIBRATION","CALIBRATION_OK","READY","WORKING"]
        self.STTHRUST_List=["PREPARING","CALIBRATION","CALIBRATION_OK","READY","WORKING"]
        self.STSERVO_List=["PREPARING","CALIBRATION","CALIBRATION_OK","READY","WORKING"]
        self.STCHU_List=["PREPARING","CALIBRATION","CALIBRATION_OK","READY","WORKING"]
        self.STCAMERA_List=["PREPARING","CAPTURE_OK","READY","SERCH_MODE","VIDEO_MODE"]
        self.STCONTROLLER_List=["PREPARING","MANUAL_CONTROL","ATTITUDE_CONTROL","AUTO_CONTROL"]
        self.STATUS=[self.STSOCKET_List,
                     self.STIMU_List,
                     self.STTHRUST_List,
                     self.STSERVO_List,
                     self.STCHU_List,
                     self.STCAMERA_List,
                     self.STCONTROLLER_List]
    
    # status -> [STSOCKET , STIMU , STTHRUST ,STSERVO , STCHU, STCAMERA]の順番
    def Encoder(self,status):
        status_num=[-1]*len(self.STATUS)
        num=0
        pos=0
        for i in self.STATUS:
            pos=0
            for j in i:
                if status[num]==j:
                    status_num[num]=pos
                
                pos+=1
            num+=1
        
        num=0
        return status_num
    
    def Decoder(self,status_num):
        status_str=["ERROR"]*len(self.STATUS)
        num=0
        for i in self.STATUS:
            if status_num[num]>=0:
                status_str[num]=i[status_num[num]]
            num+=1
        
        return status_str

        




