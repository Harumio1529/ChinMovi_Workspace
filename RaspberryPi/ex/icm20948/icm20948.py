import smbus
import time
import numpy as np
import csv
import pprint

i2c=smbus.SMBus(1)
sensor_addr=0x68

class icm20948:
    def hello(self):
        value = 0x00
        ans=i2c.read_byte_data(sensor_addr,value)
        if ans==0xEA:
            print("icm20948 connected!!")
        else :
            print("icm20948 No Connected ...")

    def setup(self):
        # set data container. it's numpy data.
        # it has 3axis data -> x y z 
        self.gy_data_raw=np.empty(3,dtype=np.int16)
        self.ac_data_raw=np.empty(3,dtype=np.int16)
        self.gy_data=np.empty(3,dtype=np.float)
        self.ac_data=np.empty(3,dtype=np.float)
        # sensor start up
        i2c.write_byte_data(sensor_addr,0x06,0x02)
        # Acc Sensor start up
        i2c.write_byte_data(sensor_addr,0x0F,0x02)
        # sensitivity
        self.ac_sf=16384.0
        self.gy_sf=131.0
    
    def set_scale_gyr(self,scale_num_gyr="250dps"):
        # change user bank
        i2c.write_byte_data(sensor_addr,0x7F,0x20)

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
        i2c.write_byte_data(sensor_addr,0x01,val)
        # change user bank
        i2c.write_byte_data(sensor_addr,0x7F,0x00)

    def set_scale_acc(self,scale_num_acc="2G"):
        # change user bank
        i2c.write_byte_data(sensor_addr,0x7F,0x20)

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
        
    ax = int(10*data[0])+4
        else :
            val=0x01
            self.ac_sf=16384.0
            print("Argument error. set scale 2G")

        # set acc scale
        i2c.write_byte_data(sensor_addr,0x14,val)
        # change user bank
        i2c.write_byte_data(sensor_addr,0x7F,0x00)

    def get_gyr(self):
        # read 6byte from 0x33
        # 3axis data is into each 2byte from 0x33
        ans = i2c.read_i2c_block_data(sensor_addr,0x33,6)
        for i in range(3):
            self.gy_data[i]=((ans[2*i] << 8 | ans[(2*i)+1]))
        print(float(self.gy_data[0])/self.gy_sf)
        print(float(self.gy_data[1])/self.gy_sf)
        print(float(self.gy_data[2])/self.gy_sf)
        print("fin")
    
    def get_acc(self):
        # read 6byte from 0x2D
        # 3axis data is into each 2byte from 0x2D
        ans = i2c.read_i2c_block_data(sensor_addr,0x2D,6)
        for i in range(3):
            self.ac_data_raw[i]=((ans[2*i] << 8 | ans[(2*i)+1]))
            self.ac_data[i]=self.ac_data_raw[i]/self.ac_sf
        # print(float(self.ac_data[0])/self.ac_sf)
        # print(float(self.ac_data[1])/self.ac_sf)
        # print(float(self.ac_data[2])/self.ac_sf)
        # print("fin")
        return np.round(self.ac_data,2)
    

    
    











sensor=icm20948()
sensor.hello()
sensor.setup()
sensor.set_scale_gyr("500dps")
sensor.set_scale_acc("2G")
# with open("/home/takuma/Desktop/ChinMovi_Workspace/RaspberryPi/ex/icm20948/log.csv","w") as f: 
#     writer=csv.writer(f)
#     while True:
#         data=sensor.get_acc()
#         writer.writerow([data[0],data[1],data[2]])
#         print(".")

while True:
    data=sensor.get_acc()
    aho = ["-" for i in range(10)]
    ax = int(10*data[0])+4
    aho[ax] = "!"
    print(f"\r{str(aho)}",end="")