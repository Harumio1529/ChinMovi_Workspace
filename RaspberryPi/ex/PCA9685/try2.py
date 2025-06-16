import smbus
import time
import math

import RPi.GPIO as GPIO

from pca9685 import PCA9685

i2c=smbus.SMBus(1)
pca9685=PCA9685(i2c)

pca9685.set_pwm_freq(250)
pca9685.set_all_pwm(0,0)
GPIO.setmode(GPIO.BCM)

GPIO.setup(20,GPIO.OUT)
GPIO.setup(21,GPIO.OUT)

start=time.time()
try :
    while True:

        pca9685.set_pwm(3,0,4000)
        GPIO.output(21,True)
        GPIO.output(20,False)
        print("move!")
        
except KeyboardInterrupt:
    pca9685.set_all_pwm(0,0)
    GPIO.output(20,False)
    GPIO.output(21,False)
    end=time.time()
    print(end-start)
