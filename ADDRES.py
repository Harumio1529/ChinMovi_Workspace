import socket
import time

def CheckIPAddress(module):
    if module=="PC":
        ip=socket.gethostbyname("raspberrypi.local")
        print(f"Found RaspberryPi. The IP Address is {ip} !!")
        client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client.connect((ip,5000))
        thisIP=client.getsockname()[0]
        print(f"This PC's IP is {thisIP} !!")
        client.close()

        # 通信チェック用のクライアント立ち上げ
        client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        client.bind((thisIP,5000))
        data=""
        while True:
            #通信確認用メッセージ送信
            msg="HelloRaspberryPi!!"
            SendData=msg.encode("utf-8")
            client.sendto(SendData,(ip,5000))
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
        client.bind(("",5000))
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


class Sensor_node:
    def __init__(self):
        self.IP="169.254.143.180"
        self.PORT=5001
        self.addres=(self.IP,self.PORT)

class PC_node:
    def __init__(self):
        self.IP="169.254.105.97"
        self.PORT=5002
        self.addres=(self.IP,self.PORT)

class Camera_node:
    def __init__(self):
        self.IP="169.254.143.180"
        self.PORT=5003
        self.addres=(self.IP,self.PORT)

class Controler_node:
    def __init__(self):
        self.IP="169.254.143.180"
        self.PORT=5004
        self.addres=(self.IP,self.PORT)

