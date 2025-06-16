import time
import RPi.GPIO as GPIO

class TB6612:
    def __init__(self,i2c,pwm_module,pwm_pin,out1,out2):
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
        try:
            while True:
                start=time.time()
                self.move_oneside(speed)
                end=time.time()
                self.MaxTime+=(end-start)
        except KeyboardInterrupt:
            print("Calibration Fin!")
            print(f"Result:{self.MaxTime:.2f}[s]")

                
    
    def move_oneside(self,speed):
        self.pca9685.set_pwm(self.pwm_pin,0,speed)
        GPIO.output(self.out1,False)
        GPIO.output(self.out2,True)
    
    def move_otherside(self,speed):
        self.pca9685.set_pwm(self.pwm_pin,0,speed)
        GPIO.output(self.out1,True)
        GPIO.output(self.out2,False)
