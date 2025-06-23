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

