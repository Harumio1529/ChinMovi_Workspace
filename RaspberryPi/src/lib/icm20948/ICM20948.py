
import time
import numpy as np



imu_addr=0x68
mag_addr=0x0C

d2r=0.017453292519

class ICM20948():
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
        # set offset num
        self.gyr_offset=[0,0,0]
        self.acc_offset=[0,0,0]
        # sensor start up
        # self.i2c.write_byte_data(imu_addr,0x06,0x00)
        self.i2c.write_byte_data(imu_addr,0x06,0x02)
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
        self.i2c.write_byte_data(imu_addr,0x7F,0x20)
        time.sleep(0.01)

        if scale_num_gyr=="250dps":
            val=0x00
            self.gy_sf=131.0

        elif scale_num_gyr=="500dps":
            val=0x02
            self.gy_sf=65.5

        elif scale_num_gyr=="1000dps":
            val=0x04
            self.gy_sf=32.8

        elif scale_num_gyr=="2000dps":
            val=0x06
            self.gy_sf=16.4

        else :
            val=0x00
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
        # print([bin(ans[0]),bin(ans[1])])
        for i in range(3):
            self.gy_data_raw[i]=((ans[(2*i)] << 8 | ans[(2*i)+1]))
            self.gy_data[i]=(self.gy_data_raw[i]/self.gy_sf)*d2r
        return [self.gy_data[0]-self.gyr_offset[0],self.gy_data[1]-self.gyr_offset[1],self.gy_data[2]-self.gyr_offset[2]]
    
    def get_acc(self):
        # read 6byte from 0x2D
        # 3axis data is into each 2byte from 0x2D
        ans = self.i2c.read_i2c_block_data(imu_addr,0x2D,6)
        for i in range(3):
            self.ac_data_raw[i]=((ans[2*i] << 8 | ans[(2*i)+1]))
            self.ac_data[i]=self.ac_data_raw[i]/self.ac_sf
        return [self.ac_data[0]-self.acc_offset[0],self.ac_data[1]-self.acc_offset[1],self.ac_data[2]-self.acc_offset[2]]
    
    def get_all(self):
        ans= self.i2c.read_i2c_block_data(imu_addr,0x2D,14)
        acX_raw=int(ans[0] << 8 | ans[1])
        acY_raw=int(ans[2] << 8 | ans[3])
        acZ_raw=int(ans[4] << 8 | ans[5])
        print([acX_raw,acY_raw,acZ_raw])


    
    def get_mag(self):
        # read 6byte from 0x11
        # 3axis data is into each 2byte from 0x11
        ans = self.i2c.read_i2c_block_data(mag_addr,0x11,8)
        for i in range(3):
            self.mag_data_raw[i]=((ans[(2*i)+1] << 8 | ans[2*i]))
            self.mag_data[i]=self.mag_data_raw[i]*self.mag_sf
        return np.round(self.mag_data_raw,2)
    
    def check_mag_data_ready(self):
        ans=self.i2c.read_byte_data(mag_addr,0x10)
        print(ans)
    
    def calibration(self,iter):
        gyr_integ=[0,0,0]
        acc_integ=[0,0,0]
        print("Dont move IMU !!")
        time.sleep(3)
        print("Calibration Start!")
        time.sleep(2)
        
        for i in range(iter):
            gyr=self.get_gyr()
            acc=self.get_acc()
            gyr_integ[0]+=gyr[0]
            gyr_integ[1]+=gyr[1]
            gyr_integ[2]+=gyr[2]
            acc_integ[0]+=acc[0]
            acc_integ[1]+=acc[1]
            acc_integ[2]+=(acc[2]-1.0)
        for k in range(3):
            self.gyr_offset[k]=gyr_integ[k]/iter
            self.acc_offset[k]=acc_integ[k]/iter


    

    
    









