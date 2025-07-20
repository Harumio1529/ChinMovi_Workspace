# コントローラ計算
class Controller():
    def __init__(self):
        self.input_srv1=2048
        self.input_srv2=2048
        self.input_th1=0
        self.input_th2=0
        self.input_th3=0
        self.input_th4=0
        self.input_chu1=0
        self.input_chu2=0

    def ManualController(self,PropoData):
        # スラスタ
        self.input_th1=int(600*PropoData[0]+1600)
        self.input_th2=int(600*PropoData[0]+1600)
        self.input_th3=int(600*PropoData[1]+1600)
        self.input_th4=int(600*PropoData[1]+1600)

        # アーム
        if PropoData[5]>=0.5:
            self.input_srv1+=10
            self.input_srv2+=10

        if PropoData[6]>=0.5:
            self.input_srv1-=9
            self.input_srv2-=9
        
        # 注射器1
        self.input_chu1=0
        self.input_chu2=0
        if PropoData[7]>=0.5:
            self.input_chu1=1
        if PropoData[8]>=0.5:
            self.input_chu1=-1
        # 注射器2
        if PropoData[9]>=0.5:
            self.input_chu2=1
        if PropoData[8]>=0.5:
            self.input_chu2=-1
    
    def ReferenceGenerator(Propodata):
        ref_roll=0.0
        ref_pitch=0.0
        ref_yaw=0.0
        return ref_roll,ref_pitch,ref_yaw


    def Attitude_PIDController(Ref,SensData):
        pass

    def FullAuto_Controller():
        pass
        

        


    def Controller(self,PropoData,SensData,CNTRLMODE):
        if CNTRLMODE=="MANUAL":
            self.ManualController(PropoData)
        elif CNTRLMODE=="ATTITUDE_CONTROL":
            self.Attitude_PIDController(PropoData,SensData)
        elif CNTRLMODE=="AUTO_CONTROL":
            self.FullAuto_Controller()
        else :
            print("use valid controll mode")
