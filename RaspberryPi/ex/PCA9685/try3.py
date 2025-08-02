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
SRV.close()

