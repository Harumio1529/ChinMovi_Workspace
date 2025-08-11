
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
        self.f0=0.1
        self.f1=2
        self.amp=0.8
        self.iter=0
        self.maxiter=20/0.01

        # PIDコントローラ
        self.ROLL=PID(0.01)
        self.PITCH=PID(0.01)
        self.YAW=PID(0.01)

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
        ref_pitch=-1*Propodata[2]*180
        ref_yaw=0.0
        return [ref_roll,ref_pitch,ref_yaw]
    

    def Attitude_PIDController(self,Ref,SensData,PIDGain):
        # ピッチング計算
        Pitching=self.PITCH.Controller(Ref[1],SensData[2][2],PIDGain[1],PIDGain[4],PIDGain[7])
        # ヨーイング計算
        Yawing=self.YAW.Controller(0,0,PIDGain[2],PIDGain[5],PIDGain[8])
        
        

        
        return [[0.0,0.0,0.0,0.0],[0.0,0.0],[0.0,0.0]]

    def FullAuto_Controller(self,PropoData):
        # import math
        # freq=self.f0+(self.f1-self.f0)*(self.iter/self.maxiter)
        # phase = 2 * math.pi * freq * self.iter
        # y=self.amp*math.sin(phase)

        # Heave=-1*y
        # Yawing=0
        # Pitching=-1*0
        # Zenshin=-0.5*(0+1)
        # Koutai=-0.5*(0+1)
        # Surge=Zenshin-Koutai

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
            return self.Attitude_PIDController(self.ReferenceGenerator(PropoData),SensData,PIDGain)
        elif CNTRLMODE=="AUTO_CONTROL":
            return self.FullAuto_Controller(PropoData)
        else :
            print("use valid controll mode")
            return [[0.0,0.0,0.0,0.0],[0.0,0.0],[0.0,0.0]]

class PID:
    def __init__(self,Ts):
        self.Ts=Ts #[s]で入力
        self.integ=0.0
        self.e_old=0.0
    
    def Controller(self,Ref,Sens,Kp,Ki,Kd):
        e_now=Ref-Sens
        #P項
        P_out=e_now*Kp
        #I項
        I_out=self.integ*Ki
        
        #D項
        diff=(e_now-self.e_old)/self.Ts
        D_out=diff*Kd

        self.integ+=0.5*(e_now+self.e_old)*self.Ts #台形積分
        self.e_old=e_now

        return P_out+I_out+D_out+I_out