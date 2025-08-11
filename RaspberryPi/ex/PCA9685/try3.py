import smbus
import time
import math

import RPi.GPIO as GPIO

from pca9685 import SERVO


i2c=smbus.SMBus(1)


 # サーボモジュール起動
SRV=SERVO(i2c,4,5,False)
# キャリブレーション（と言ってるが動かしてるだけ）
SRV.Caribration()
i=0
input=0
try:
    while True:
        input=int(2000*math.sin(i*0.01)+2000)
        SRV.set_servo(input,input)
        print(input)
        i+=0.1
except KeyboardInterrupt:
    SRV.close()
    print("fin")


