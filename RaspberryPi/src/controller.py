
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

        # モデル同定用
        self.duration=20
        self.f0=5
        self.f1=20
        self.amp=0.8
        self.iter=0
        self.maxiter=20/0.01

    def ManualController(self,PropoData):
        self.iter=0
        # print(PropoData)
        Heave=-1*PropoData[0]
        Yawing=PropoData[1]
        Pitching=-1*PropoData[2]
        Zenshin=-0.5*(PropoData[3]+1)
        Koutai=-0.5*(PropoData[4]+1)
        Surge=Zenshin-Koutai

        # スラスタ
        self.input_th1=int(-600*(Surge+Yawing)+1600)
        self.input_th2=int(600*(Surge-Yawing)+1600)
        self.input_th3=int(600*(Pitching+Heave)+1600)
        self.input_th4=int(600*(-Pitching+Heave)+1600)
        input_th_all=[self.input_th1,self.input_th2,self.input_th3,self.input_th4]

        # アーム
        if PropoData[5]>=0.5:
            self.input_srv1=2800  #値大で閉じる
            self.input_srv2=600   #値小で閉じる

        if PropoData[6]>=0.5:
            self.input_srv1=1300
            self.input_srv2=2100
        input_srv_all=[self.input_srv1,self.input_srv2]
        
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
        input_chu_all=[self.input_chu1,self.input_chu2]
        
        return [input_th_all,input_srv_all,input_chu_all]
    
    def ReferenceGenerator(Propodata):
        ref_roll=0.0
        ref_pitch=0.0
        ref_yaw=0.0
        return ref_roll,ref_pitch,ref_yaw


    def Attitude_PIDController(self,Ref,SensData,PIDGain):
        print(PIDGain)
        return [[0.0,0.0,0.0,0.0],[0.0,0.0],[0.0,0.0]]

    def FullAuto_Controller(self):
        import math
        freq=self.f0+(self.f1-self.f0)*(self.iter/self.maxiter)
        phase = 2 * math.pi * freq * self.iter
        y=self.amp*math.sin(phase)

        Heave=-1*y
        Yawing=0
        Pitching=-1*0
        Zenshin=-0.5*(0+1)
        Koutai=-0.5*(0+1)
        Surge=Zenshin-Koutai

        # スラスタ
        self.input_th1=int(-600*(Surge+Yawing)+1600)
        self.input_th2=int(600*(Surge-Yawing)+1600)
        self.input_th3=int(600*(Pitching+Heave)+1600)
        self.input_th4=int(600*(-Pitching+Heave)+1600)
        input_th_all=[self.input_th1,self.input_th2,self.input_th3,self.input_th4]

        input_srv_all=[self.input_srv1,self.input_srv2]
        input_chu_all=[self.input_chu1,self.input_chu2]

        # iter reset
        if self.iter<=self.maxiter:
            self.iter+=1



        return [input_th_all,input_srv_all,input_chu_all]
        

        


    def Controller(self,PropoData,SensData,PIDGain,CNTRLMODE):
        
        if CNTRLMODE=="MANUAL_CONTROL":
            return self.ManualController(PropoData)
        elif CNTRLMODE=="ATTITUDE_CONTROL":
            return self.Attitude_PIDController(PropoData,SensData,PIDGain)
        elif CNTRLMODE=="AUTO_CONTROL":
            return self.FullAuto_Controller()
        else :
            print("use valid controll mode")
            return [[0.0,0.0,0.0,0.0],[0.0,0.0],[0.0,0.0]]