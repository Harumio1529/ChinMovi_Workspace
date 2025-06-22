import sys
import os
import socket

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"../../..")))
import ADDRES

ip=socket.gethostbyname("raspberrypi.local")
print(f"Found RaspberryPi. The IP Address is {ip} !!")

client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client.connect((ip,5000))
thisIP=client.getsockname()[0]

print(thisIP)
