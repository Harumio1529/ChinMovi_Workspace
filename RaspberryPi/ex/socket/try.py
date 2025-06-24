import socket
import time
import pickle

from COMMON import Sensor_node,Camera_node,Controler_node,PC_node

#登場するノードを定義
ECU=Controler_node()

sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# server_addr=("192.168.1.16",49300)
server_addr=(ECU.IP,ECU.PORT)
sock.bind(server_addr)

try :
    while True:
        msg,addr=sock.recvfrom(1024)
        propodata=pickle.loads(msg)
        print(propodata)

except KeyboardInterrupt:
    print("fin")



