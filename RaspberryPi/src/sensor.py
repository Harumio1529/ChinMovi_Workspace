import socket
import time
import pickle
import smbus
from COMMON import Sensor_node,PC_node

from lib.icm20948 import ICM20948
from lib.madgwickfilter import madgwickahrs

i2c=smbus.SMBus(1)
NodeAddres=Sensor_node()
PC=PC_node()
IMU=ICM20948.ICM20948(i2c)
estimate=madgwickahrs.MadgwickAHRS(sampleperiod=0.01,beta=1.0)

# UDP通信クライアント設立
#client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
#client.bind(NodeAddres.addres)

def main_worker():
    # センサ値取得
    gyr=IMU.get_gyr()
    acc=IMU.get_acc()
    estimate.update_imu(gyr,acc)
    euler=estimate.quaternion.to_euler_angles_ZYX()
    data=[gyr[0],gyr[1],gyr[2],acc[0],acc[1],acc[2],euler[0],euler[1],euler[2]]
    # PCへ送信
    Send_Data=pickle.dumps(data)
    #client.sendto(Send_Data,PC.addres)
    print(data)

# 定周期大麻
def scheduler(interval, func):
    base_time = time.time()
    next_time = 0
    while True:
        func()
        next_time = ((base_time - time.time()) % interval) or interval
        time.sleep(next_time)

IMU.hello()
IMU.setup()
IMU.set_scale_gyr("500dps")
IMU.set_scale_acc("2G")
IMU.calibration(1000)
scheduler(0.01,main_worker)
