import smbus
import time
import math

from pca9685 import PCA9685

i2c=smbus.SMBus(1)
pca9685=PCA9685(i2c)

pca9685.set_pwm_freq(250)
# pca9685.set_pwm(0,0,2000)
pca9685.set_pwm(0,0,1000)
time.sleep(1)
print("up")
# pca9685.set_pwm(0,0,200)
pca9685.set_pwm(0,0,100)
time.sleep(1)
print("lo")
omega=0
try :
    while True:
        
        data=int(600*math.sin(omega*0.01)+1600)
        pca9685.set_pwm(0,0,data)
        print(data)
        time.sleep(0.1)
        omega+=1
except KeyboardInterrupt:
    pca9685.set_all_pwm(0,0)