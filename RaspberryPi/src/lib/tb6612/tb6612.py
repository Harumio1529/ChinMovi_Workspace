import time
import RPi.GPIO as GPIO
import keyboard

class TB6612:
    def __init__(self,i2c,pwm_module,pwm_pin,out1,out2,LimitEnable=False):
        self.LimitEnable=LimitEnable
        self.pca9685=pwm_module(i2c)
        self.pca9685.set_pwm_freq(250)
        self.pca9685.set_all_pwm(0,0)
        GPIO.setmode(GPIO.BCM)
        self.out1=out1
        self.out2=out2
        self.pwm_pin=pwm_pin
        GPIO.setup(self.out1,GPIO.OUT)
        GPIO.setup(self.out2,GPIO.OUT)
    
    def time_calibration(self,speed):
        self.MaxTime=0
        print("StartCalibration!")
        time.sleep(2)
        print("3")
        time.sleep(1)
        print("2")
        time.sleep(1)
        print("1")
        time.sleep(1)
        print("start!")
        while True:
            start=time.time()
            self.pca9685.set_pwm(self.pwm_pin,0,speed)
            GPIO.output(self.out1,False)
            GPIO.output(self.out2,True)
            end=time.time()
            self.MaxTime+=(end-start)
            if(keyboard.is_pressed("space")):
                break
        print("Calibration Fin!")
        print(f"Result:{self.MaxTime:.2f}[s]")

                
    # Limitがかかった場合はTrue Limit内にいる場合はFalse
    def move_oneside(self,speed):
        start=time.time()
        if self.LimitEnable==True and self.MaxTime<=self.LimitTime_oneside:
            GPIO.output(self.out1,False)
            GPIO.output(self.out2,False)
            return True
        self.pca9685.set_pwm(self.pwm_pin,0,speed)
        GPIO.output(self.out1,False)
        GPIO.output(self.out2,True)
        end=time.time()
        self.LimitTime_oneside+=(end-start)
        self.LimitTime_otherside-=(end-start)
        return False
            
    # Limitがかかった場合はTrue Limit内にいる場合はFalse
    def move_otherside(self,speed):
        start=time.time()
        if self.LimitEnable==True and self.MaxTime<=self.LimitTime_otherside:
            GPIO.output(self.out1,False)
            GPIO.output(self.out2,False)
            return True
        self.pca9685.set_pwm(self.pwm_pin,0,speed)
        GPIO.output(self.out1,True)
        GPIO.output(self.out2,False)
        end=time.time()
        self.LimitTime_otherside+=(end-start)
        self.LimitTime_oneside-=(end-start)
        return False
