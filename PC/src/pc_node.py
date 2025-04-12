import socket
import time
import pickle

from ADDRES import Sensor_node,Camera_node,Controler_node

#登場するノードを定義
Sensor=Sensor_node()
Camera=Camera_node()
Controler=Controler_node()


client=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
message=1
while True:
    try:
        
        #センサデータ取得
        # start_sensor=time.perf_counter()
        client.sendto(str(message).encode(encoding='utf-8'),(Sensor.IP,Sensor.PORT))
        data,addr=client.recvfrom(1024)
        sensor_data=pickle.loads(data)
        # end_sensor=time.perf_counter()
        #カメラデータ取得
        # start_camera=time.perf_counter()
        # client.sendto(str(message).encode(encoding='utf-8'),(Camera.IP,Camera.PORT))
        # data,addr=client.recvfrom(1024)
        # camera_data=data.decode(encoding="utf-8")
        # end_camera=time.perf_counter()
        # print(sensor_data+","+camera_data)
        # print(str(end_sensor-start_sensor)+","+str(end_camera-start_camera))
        print(sensor_data)
        time.sleep(1)

    except KeyboardInterrupt:
        client.close()
        break