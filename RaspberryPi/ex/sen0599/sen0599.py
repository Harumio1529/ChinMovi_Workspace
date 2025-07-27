import serial
import serial.tools.list_ports
import numpy as np
import time

class sen0599():
    def __init__(self):
        baud=115200
        prty=serial.PARITY_NONE
        port='/dev/serial0'
        self.cmd=bytes([0x55])
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
            data=self.Serial.read(1)
            if data and (data[0]==0xff):
                self.buffer[0]=0xff
                for i in range(3):
                    data=self.Serial.read(1)
                    if data:
                        self.buffer[i+1]=data[0]
                CS=self.buffer[0]+self.buffer[1]+self.buffer[2]
                if self.buffer[3]==(CS & 0xFF):
                    Dist=(self.buffer[1]<<8) + self.buffer[2]
        
        return Dist
    

if __name__=="__main__":
    sens=sen0599()
    while True:
        a=sens.read_data()
        print(a)