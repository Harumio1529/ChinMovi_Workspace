import pygame

# 信号の不感帯を設定
def set_Fukantai(data,F_Big,F_Small):
    if F_Small<=data and data<=F_Big:
        data=0
    return data


class ps4():
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        self.propo=pygame.joystick.Joystick(0)
        self.propo.init()
    
    def getPropoData(self):
        data=[0]*4
        pygame.event.get()
        for i in range(4):
            data[i]=set_Fukantai(self.propo.get_axis(i),0.1,-0.1)
        return data
            
