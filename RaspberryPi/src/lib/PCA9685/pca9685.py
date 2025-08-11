import time
import math

pwm_addr=0x40

LED0_ON_L          = 0x06
LED0_ON_H          = 0x07
LED0_OFF_L         = 0x08
LED0_OFF_H         = 0x09

ALL_LED_ON_L       = 0xFA
ALL_LED_ON_H       = 0xFB
ALL_LED_OFF_L      = 0xFC
ALL_LED_OFF_H      = 0xFD

Fs=250

class PCA9685():
    def __init__(self,module):
        # define i2c module
        self.i2c=module
        # wake up and set up 
        self.i2c.write_byte_data(pwm_addr,0x01,0x04)
        time.sleep(0.01)
        self.i2c.write_byte_data(pwm_addr,0x00,0x01)
        time.sleep(0.01)
        mode1=self.i2c.read_byte_data(pwm_addr,0x00)
        mode1=mode1 & ~0x10
        self.i2c.write_byte_data(pwm_addr,0x00,mode1)
        time.sleep(0.01)
        self.set_all_pwm(0,0)
    
    def set_pwm_freq(self,freq_hz):
        prescaleval = 25000000.0    # 25MHz
        prescaleval /= 4096.0       # 12-bit
        prescaleval /= float(freq_hz)
        prescaleval -= 1.0
        prescale = int(math.floor(prescaleval + 0.5))
        oldmode=self.i2c.read_byte_data(pwm_addr,0x00)
        newmode=(oldmode & 0x7F) | 0x10
        self.i2c.write_byte_data(pwm_addr,0x00,newmode)
        time.sleep(0.01)
        self.i2c.write_byte_data(pwm_addr,0xFE,prescale)
        time.sleep(0.01)
        self.i2c.write_byte_data(pwm_addr,0x00,oldmode)
        time.sleep(0.01)
        self.i2c.write_byte_data(pwm_addr,0x00,(oldmode | 0x80))
        time.sleep(0.01)

    def set_pwm(self,channel,on,off):
        self.i2c.write_byte_data(pwm_addr,LED0_ON_L+4*channel,(on & 0xFF))
        self.i2c.write_byte_data(pwm_addr,LED0_ON_H+4*channel,(on >> 8))
        self.i2c.write_byte_data(pwm_addr,LED0_OFF_L+4*channel,(off & 0xFF))
        self.i2c.write_byte_data(pwm_addr,LED0_OFF_H+4*channel,(off >> 8))

    def set_all_pwm(self,on,off):
        self.i2c.write_byte_data(pwm_addr,ALL_LED_ON_L,(on & 0xFF))
        self.i2c.write_byte_data(pwm_addr,ALL_LED_ON_H,(on >> 8))
        self.i2c.write_byte_data(pwm_addr,ALL_LED_OFF_L,(off & 0xFF))
        self.i2c.write_byte_data(pwm_addr,ALL_LED_OFF_H,(off >> 8))

class THRUSTER(PCA9685):
    # コンストラクタの引数には各スラスタを挿したピンの番号を記入        
    def __init__(self,module,PinNum_Th1,PinNum_Th2,PinNum_Th3,PinNum_Th4,DEBUG_PRINT):
        super().__init__(module)
        # pwm周波数を定義
        self.set_pwm_freq(Fs)
        self.PinTh1=PinNum_Th1
        self.PinTh2=PinNum_Th2
        self.PinTh3=PinNum_Th3
        self.PinTh4=PinNum_Th4
        self.Limitter_MAX=2200
        self.Limitter_MIN=1000
        self.DP=DEBUG_PRINT
    
    def debugprint(self,data):
        if self.DP:
            print(data)
    
    def Calibration(self):
        self.set_pwm(self.PinTh1,0,1000)
        self.set_pwm(self.PinTh2,0,1000)
        self.set_pwm(self.PinTh3,0,1000)
        self.set_pwm(self.PinTh4,0,1000)
        self.debugprint("Hi Level")
        time.sleep(1)
        self.set_pwm(self.PinTh1,0,100)
        self.set_pwm(self.PinTh2,0,100)
        self.set_pwm(self.PinTh3,0,100)
        self.set_pwm(self.PinTh4,0,100)
        self.debugprint("Lo Level")
        time.sleep(1)
        return "CALIBRATION_OK"


    def Limitter(self,val):
        return max(min(val,self.Limitter_MAX),self.Limitter_MIN)
    
    def set_thrust(self,Th1,Th2,Th3,Th4):
        self.set_pwm(self.PinTh1,0,self.Limitter(int(Th1)))
        self.set_pwm(self.PinTh2,0,self.Limitter(int(Th2)))
        self.set_pwm(self.PinTh3,0,self.Limitter(int(Th3)))
        self.set_pwm(self.PinTh4,0,self.Limitter(int(Th4)))
    
    def close(self):
        self.set_pwm(self.PinTh1,0,0)
        self.set_pwm(self.PinTh2,0,0)
        self.set_pwm(self.PinTh3,0,0)
        self.set_pwm(self.PinTh4,0,0)

class SERVO(PCA9685):
    # コンストラクタにはサーボを挿したピンの番号を記入
    def __init__(self, module,PinNum_Srv1,PinNum_Srv2,DEBUG_PRINT):
        super().__init__(module)
        self.set_pwm_freq(Fs)
        self.PinSrv1=PinNum_Srv1
        self.PinSrv2=PinNum_Srv2
        self.Limitter_MAX=4095
        self.Limitter_MIN=0
        self.DP=DEBUG_PRINT
    
    def debugprint(self,data):
        if self.DP:
            print(data)
    
    def Limitter(self,val):
        return max(min(val,self.Limitter_MAX),self.Limitter_MIN)
    
    def set_servo(self,Srv1,Srv2):
        self.set_pwm(self.PinSrv1,0,self.Limitter(int(Srv1)))
        self.set_pwm(self.PinSrv2,0,self.Limitter(int(Srv2)))
    
    def Caribration(self):
        # self.set_servo(2048,2048)
        time.sleep(2)
        self.set_servo(1,1)
        time.sleep(2)
        # self.set_servo(4095,4095)
        time.sleep(2)
        return "CARIBRATION_OK"
    
    def close(self):
        self.set_pwm(self.PinSrv1,0,0)
        self.set_pwm(self.PinSrv2,0,0)

        

        

