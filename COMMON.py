import socket
import time

TestPort=5000
RasPiPort=5001
PCPort=5002

def CheckIPAddress(module):
    if module=="PC":
        ip=socket.gethostbyname("raspberrypi.local")
        print(f"Found RaspberryPi. The IP Address is {ip} !!")
        client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client.connect((ip,TestPort))
        thisIP=client.getsockname()[0]
        print(f"This PC's IP is {thisIP} !!")
        client.close()

        # 通信チェック用のクライアント立ち上げ
        client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client.bind((thisIP,TestPort))
        data=""
        while True:
            #通信確認用メッセージ送信
            msg="HelloRaspberryPi!!"
            SendData=msg.encode("utf-8")
            client.sendto(SendData,(ip,TestPort))
            print("Check Connect...")
            data,addr=client.recvfrom(1024)
            time.sleep(2)
            
            if data.decode("utf-8")=="HelloPC!!":
                # 終了処理
                client.close()
                break
        print("socket com is OK.")
        print(f"RaspberryPi's IP is {addr}")
        return addr
    
    elif module=="RaspberryPi":
        client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client.bind(("",TestPort))
        data=""
        while True:
            print("Check Connect...")
            data,addr=client.recvfrom(1024)
            
            if data.decode("utf-8")=="HelloRaspberryPi!!":
                # 返送用メッセージ送信
                msg="HelloPC!!"
                SendData=msg.encode("utf-8")
                client.sendto(SendData,addr)
                break
        client.close()
        print("socket com is OK.")
        print(f"PC's IP is {addr}")
        return addr
    
    else:
        print("The augument is invalid. Set PC or RaspberryPi")


class RasPi:
    def __init__(self,IP):
        self.IP=IP
        self.RasPi_Port=RasPiPort
        self.address=(self.IP,self.RasPi_Port)

class PC:
    def __init__(self,IP):
        self.IP=IP
        self.PC_Port=PCPort
        self.address=(self.IP,self.PC_Port)
        

class StatusAnalyzer:
    def __init__(self):
        self.STSOCKET_List=["PREPARING","COM_OK","STANDUP_COMAGENT","READY"]
        self.STIMU_List=["PREPARING","SETUP","CALIBRATION","CALIBRATION_OK","READY","WORKING"]
        self.STTHRUST_List=["PREPARING","CALIBRATION","CALIBRATION_OK","READY"]
        self.STSERVO_List=["PREPARING","CARIBRATION","CARIBRATION_OK","READY"]
        self.STCHU_List=["PREPARING","CARIBRATION","CARIBRATION_OK","READY"]
    
    # status -> [STSOCKET , STIMU , STTHRUST ,STSERVO , STCHU]の順番
    def Encoder(self,status):
        STATUS=[self.STSOCKET_List,self.STIMU_List,self.STTHRUST_List,self.STSERVO_List,self.STCHU_List]
        status_num=[-1,-1,-1,-1,-1]
        num=0
        pos=0
        for i in STATUS:
            pos=0
            for j in i:
                if status[num]==j:
                    status_num[num]=pos
                
                pos+=1
            num+=1
        
        num=0
        return status_num
    
    def Decoder(self,status_num):
        STATUS=[self.STSOCKET_List,self.STIMU_List,self.STTHRUST_List,self.STSERVO_List,self.STCHU_List]
        status_str=["ERROR","ERROR","ERROR","ERROR","ERROR"]
        num=0
        for i in STATUS:
            if status_num[num]>=0:
                status_str[num]=i[status_num[num]]
            num+=1
        
        return status_str
        




