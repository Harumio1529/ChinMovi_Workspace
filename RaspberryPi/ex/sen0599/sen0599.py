import serial
import serial.tools.list_ports
import numpy as np
import time

class sen0599():
    def __init__(self):
        baud=115200
        prty="N"
        port='/dev/serial0'
        self.cmd=0x55
        self.buffer=np.empty(4,dtype=np.uint8)
        self.Serial=serial.Serial(port=port,
                                  baudrate=baud,
                                  parity=prty)
    
    def read_data(self):
        CS=0
        Dist=-1
        self.Serial.write(self.cmd)
        time.sleep(0.1)
        if (self.Serial.in_waiting>0):
            time.sleep(0.004)
            if (self.Serial.read(1)==0xff):
                self.buffer[0]=0xff
                for i in range(3):
                    self.buffer[i+1]=self.Serial.read(1)
                CS=self.buffer[0]+self.buffer[1]+self.buffer[2]
                if self.buffer[3]==CS:
                    Dist=(self.buffer[1]<<8) + self.buffer[2]
        
        return Dist
    

if __name__=="__main__":
    sens=sen0599()
    while True:
        print(sens.read_data())