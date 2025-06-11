class PID_Controler:

    def calc_input(con):
        data=[0]*4
        for i in range(4):
            # お試しでpwm1000~3000の間で検証
            data[i]=1000*con[i]+2000
        return data
        
