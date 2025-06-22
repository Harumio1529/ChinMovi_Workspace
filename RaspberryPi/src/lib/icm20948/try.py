from ICM20948 import icm20948
import smbus
import time
import csv

from lib.madgwickfilter import madgwickahrs

i2c=smbus.SMBus(1)
sensor=icm20948(i2c)
estimate=madgwickahrs.MadgwickAHRS(sampleperiod=0.01,beta=1.0)
sensor.hello()
sensor.setup()
sensor.set_scale_gyr("500dps")
sensor.set_scale_acc("2G")
sensor.calibration(1000)
with open("/home/takuma/Desktop/ChinMovi_Workspace/RaspberryPi/ex/icm20948/log.csv","w") as f: 
    writer=csv.writer(f)
#     while True:
#         data=sensor.get_acc()
#         writer.writerow([data[0],data[1],data[2]])
#         print(".")

# while True:
#     data=sensor.get_acc()
#     aho = ["-" for i in range(10)]
#     ax = int(10*data[0])+4
#     aho[ax] = "!"
#     print(f"\r{str(aho)}",end="")
    while True:
        # gyr=[0,0,0]
        # acc=[0,0,1]
        gyr=sensor.get_gyr()
        acc=sensor.get_acc()
        #estimate.update_imu(gyr,acc)
        # print(sensor.get_gyr())
        # print(sensor.get_acc())
        # sensor.get_gyr()
        time.sleep(0.01)
        # sensor.check_mag_data_ready()
        #data=estimate.quaternion.to_euler_angles_ZYX()
        writer.writerow([data[0],data[1],data[2],gyr[0],gyr[1],gyr[2],acc[0],acc[1],acc[2]])
        print(gyr)
    
    
