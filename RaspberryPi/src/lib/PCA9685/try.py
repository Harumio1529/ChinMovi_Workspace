import smbus
import time
import math

from pca9685 import PCA9685

i2c=smbus.SMBus(1)
pca9685=PCA9685(i2c)
Fs = 250

pca9685.set_pwm_freq(Fs)
pca9685.set_pwm(0,0,1000)
pca9685.set_pwm(1,0,1000)
pca9685.set_pwm(2,0,1000)
pca9685.set_pwm(3,0,1000)
time.sleep(1)
print("up")
pca9685.set_pwm(0,0,100)
pca9685.set_pwm(1,0,100)
pca9685.set_pwm(2,0,100)
pca9685.set_pwm(3,0,100)
time.sleep(1)
print("lo")
omega=0
try :
    while True:
        
        data=int((410)*math.sin(omega*0.01)+1600)
        pca9685.set_pwm(0,0,data)
        print(data)
        #pca9685.set_pwm(1,0,data)
        #pca9685.set_pwm(2,0,data)
        # pca9685.set_pwm(15,0,100)
        # pca9685.set_pwm(5,0,3000)
        # time.sleep(1)
        # print(1000)
        # pca9685.set_pwm(4,0,3010)
        # time.sleep(1)
        # pca9685.set_pwm(15,0,3000)
        # pca9685.set_pwm(5,0,100)
        # time.sleep(1)
        # print(2000)
        time.sleep(0.1)
        omega+=1
except KeyboardInterrupt:
    pca9685.set_all_pwm(0,0)
