import smbus
import time
import numpy as np
import csv
import pprint


imu_addr=0x68
mag_addr=0x0C

class icm20948:
    def __init__(self,module):
        self.i2c=module

    def hello(self):
        value = 0x00
        ans=self.i2c.read_byte_data(imu_addr,value)
        if ans==0xEA:
            print("icm20948 connected!!")
        else :
            print("icm20948 No Connected ...")
    
    def hello_mag(self):
        ans=self.i2c.read_byte_data(mag_addr,0x00)
        if ans==0x48:
            print("AK09916 connected!!")
        else :
            print("AK09916 No Connected ...")


    def setup(self):
        # set data container. it's numpy data.
        # it has 3axis data -> x y z 
        self.gy_data_raw=np.empty(3,dtype=np.int16)
        self.ac_data_raw=np.empty(3,dtype=np.int16)
        self.mag_data_raw=np.empty(3,dtype=np.int16)
        self.gy_data=np.empty(3,dtype=np.float)
        self.ac_data=np.empty(3,dtype=np.float)
        self.mag_data=np.empty(3,dtype=np.int16)
        # sensor start up
        self.i2c.write_byte_data(imu_addr,0x06,0x00)
        time.sleep(0.01)
        # Acc Sensor start up
        self.i2c.write_byte_data(imu_addr,0x0F,0x02)
        time.sleep(0.01)
        # sensitivity
        self.ac_sf=16384.0
        self.gy_sf=131.0
        self.mag_sf=0.15

    def set_freq_mag(self):
        # 100HZ logging
        self.i2c.write_byte_data(mag_addr,0x31,0x08)
        time.sleep(0.01)
    
    def set_scale_gyr(self,scale_num_gyr="250dps"):
        # change user bank
        self.i2c.write_byte_data(imu_addr,0x7F,0x02)
        time.sleep(0.01)

        if scale_num_gyr=="250dps":
            val=0x01
            self.gy_sf=131.0

        elif scale_num_gyr=="500dps":
            val=0x03
            self.gy_sf=65.5

        elif scale_num_gyr=="1000dps":
            val=0x05
            self.gy_sf=32.8

        elif scale_num_gyr=="2000dps":
            val=0x07
            self.gy_sf=164

        else :
            val=0x01
            self.gy_sf=131.0
            print("Argument error. set scale 250dps")

        # set acc scale
        self.i2c.write_byte_data(imu_addr,0x01,val)
        time.sleep(0.01)
        # change user bank
        self.i2c.write_byte_data(imu_addr,0x7F,0x00)
        time.sleep(0.01)

    def set_scale_acc(self,scale_num_acc="2G"):
        # change user bank
        self.i2c.write_byte_data(imu_addr,0x7F,0x20)
        time.sleep(0.01)

        if scale_num_acc=="2G":
            val=0x01
            self.ac_sf=16384.0

        elif scale_num_acc=="4G":
            val=0x03
            self.ac_sf=8192.0

        elif scale_num_acc=="8G":
            val=0x05
            self.ac_sf=4096.0

        elif scale_num_acc=="16G":
            val=0x07
        else :
            val=0x01
            self.ac_sf=16384.0
            print("Argument error. set scale 2G")

        # set acc scale
        self.i2c.write_byte_data(imu_addr,0x14,val)
        time.sleep(0.01)
        # change user bank
        self.i2c.write_byte_data(imu_addr,0x7F,0x00)
        time.sleep(0.01)

    def get_gyr(self):
        # read 6byte from 0x33
        # 3axis data is into each 2byte from 0x33
        ans = self.i2c.read_i2c_block_data(imu_addr,0x33,6)
        for i in range(3):
            self.gy_data[i]=((ans[2*i] << 8 | ans[(2*i)+1]))
        print(float(self.gy_data[0])/self.gy_sf)
        print(float(self.gy_data[1])/self.gy_sf)
        print(float(self.gy_data[2])/self.gy_sf)
        print("fin")
    
    def get_acc(self):
        # read 6byte from 0x2D
        # 3axis data is into each 2byte from 0x2D
        ans = self.i2c.read_i2c_block_data(imu_addr,0x2D,6)
        for i in range(3):
            self.ac_data_raw[i]=((ans[2*i] << 8 | ans[(2*i)+1]))
            self.ac_data[i]=self.ac_data_raw[i]/self.ac_sf
        # print(float(self.ac_data[0])/self.ac_sf)
        # print(float(self.ac_data[1])/self.ac_sf)
        # print(float(self.ac_data[2])/self.ac_sf)
        # print("fin")
        return np.round(self.ac_data,2)
    
    def get_mag(self):
        # read 6byte from 0x11
        # 3axis data is into each 2byte from 0x11
        ans = self.i2c.read_i2c_block_data(mag_addr,0x11,8)
        for i in range(3):
            self.mag_data_raw[i]=((ans[(2*i)+1] << 8 | ans[2*i]))
            self.mag_data[i]=self.mag_data_raw[i]*self.mag_sf
        # print(float(self.ac_data[0])/self.ac_sf)
        # print(float(self.ac_data[1])/self.ac_sf)
        # print(float(self.ac_data[2])/self.ac_sf)
        # print("fin")
        # print(ans)
        return np.round(self.mag_data_raw,2)
    
    def check_mag_data_ready(self):
        ans=self.i2c.read_byte_data(mag_addr,0x10)
        print(ans)


    

    
    










i2c=smbus.SMBus(1)
sensor=icm20948(i2c)
sensor.hello()
sensor.setup()
sensor.set_scale_gyr("500dps")
sensor.set_scale_acc("2G")
sensor.hello_mag()
sensor.set_freq_mag()
# with open("/home/takuma/Desktop/ChinMovi_Workspace/RaspberryPi/ex/icm20948/log.csv","w") as f: 
#     writer=csv.writer(f)
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
    data=sensor.get_mag()
    # sensor.check_mag_data_ready()
    time.sleep(0.1)
    print(data)