from lib.PCA9685.pca9685 import PCA9685
from lib.tb6612 import tb6612

import smbus

i2c=smbus.SMBus(1)
pwm=PCA9685

Chusyaki=tb6612.TB6612(i2c,pwm,3,20,21,LimitEnable=True)

Chusyaki.time_calibration(3000)