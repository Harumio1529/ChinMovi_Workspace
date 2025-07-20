import pygame

# 信号の不感帯を設定
def set_Fukantai(data,F_Big,F_Small):
    if F_Small<=data and data<=F_Big:
        data=0
    return data


class ps4():
    def __init__(self,stknum,btnnum):
        pygame.init()
        pygame.joystick.init()
        self.propo=pygame.joystick.Joystick(0)
        self.propo.init()
        self.sticknum=stknum
        self.buttonnum=btnnum
    
    def getPropoData(self):
        data=[0]*(self.sticknum+self.buttonnum)
        pygame.event.get()
        for i in range(self.sticknum):
            data[i]=set_Fukantai(self.propo.get_axis(i),0.1,-0.1)
        for k in range(self.buttonnum):
            data[self.sticknum+k]=self.propo.get_button(k)
        return data

def main():
    Propo=ps4()
    PropoData=Propo.getPropoData()
    time.sleep(0.01)
    print(PropoData)



if __name__ == "__main__":
    import time
    PropoData=[0]*4
    while True:
        main()