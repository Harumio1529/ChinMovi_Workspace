import socket
import time
import pickle
from ADDRES import Sensor_node

NodeAddres=Sensor_node()

# UDP通信クライアント設立
client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client.bind(NodeAddres.addres)

# 送信先アドレス
