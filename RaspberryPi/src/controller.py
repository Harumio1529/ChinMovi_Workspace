import time

# コントローラ計算
class Controller():
    def __init__(self,SA):
        # statusanalyzer
        self.SA=SA

        self.input_srv1=2048
        self.input_srv2=2048
        self.input_th1=1600
        self.input_th2=1600
        self.input_th3=1600
        self.input_th4=1600
        self.input_chu1=0
        self.input_chu2=0

        # 水中判定深度
        self.dep_underwater=0.3
        # 水中フラグ
        self.UnderWaterFlg=False
        # 深度基準点
        self.dep_base=0.8
        # 基準深度到達判定
        self.dep_reach_num=0

        # PIDコントローラ
        self.PITCH=PID(0.01)
        self.YAW=PID(0.01)
        self.HEAVE=PID(0.01)

        # PIDゲイン
        self.KpDep=0
        self.KiDep=0
        self.KdDep=0
        self.KpPitch=0
        self.KiPitch=0
        self.KdPitch=0
        self.KpYaw=0
        self.KiYaw=0
        self.KdYaw=0

        self.d_heave=0


    def ManualController(self,PropoData):
        self.iter=0
        # print(PropoData)
        # 上下
        Heave=-1*PropoData[0]
        Yawing=PropoData[1]
        Pitching=-1*PropoData[2]
        Zenshin=-0.5*(PropoData[3]+1)
        Koutai=-0.5*(PropoData[4]+1)
        # 前後
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
        
        return [*input_th_all,*input_srv_all,*input_chu_all]
    
    def ReferenceGenerator_fromPropo(self,Propodata):
        # オイラー角
        ref_roll=0.0
        ref_pitch=-1*Propodata[2]*50
        ref_yaw=0.0
        # ヒーブ
        if Propodata[0]>0.5:
            self.d_heave+=0.05
        elif Propodata[0]<0.5:
            self.d_heave-=0.05
        ref_heave=self.dep_base+self.d_heave
        # サージ
        Zenshin=-0.5*(Propodata[3]+1)
        Koutai=-0.5*(Propodata[4]+1)
        # 前後
        ref_serge=Zenshin-Koutai
        return [ref_roll,ref_pitch,ref_yaw,ref_heave,ref_serge]
    

    def Attitude_PIDController(self,Ref,SensData):
        # ピッチング計算
        Pitching=self.PITCH.Control(Ref[1],SensData[7],self.KpPitch,self.KiPitch,self.KdPitch)
        # ヨーイング計算
        # ドリフトするのでヨー制御は無効
        Yawing=self.YAW.Control(0,0,self.KpYaw,self.KiYaw,self.KdYaw)
        # ヒーブ計算
        Heave=self.HEAVE.Control(Ref[3],SensData[9],self.KpDep,self.KiDep,self.KdDep)
        # サージ計算(プロポのデータをそのままぶち込む)
        Surge=Ref[4]

        self.input_th1=int(-600*(Surge+Yawing)+1600)
        self.input_th2=int(600*(Surge-Yawing)+1600)
        self.input_th3=int(600*(Pitching+Heave)+1600)
        self.input_th4=int(600*(-Pitching+Heave)+1600)
        input_th_all=[self.input_th1,self.input_th2,self.input_th3,self.input_th4]
        # print(input_th_all)

        input_srv_all=[self.input_srv1,self.input_srv2]
        input_chu_all=[self.input_chu1,self.input_chu2]
        
        return [*input_th_all,*input_srv_all,*input_chu_all]

    def FullAuto_Controller(self,SensData,CameraData,CNTRLMODE):
        # ステートマシンで現在のモードを確認して上書きする
        CNTRLMODE=self.StateMachine(SensData,CameraData,CNTRLMODE)

        # AutoControlの時の処理
        if CNTRLMODE=="AUTO_CONTROL":
            [Pitching,Yawing,Heave,Surge]=[0.0,0.0,0.0,0.0]


        # Preparingの時の処理
        if CNTRLMODE=="FULLAUTO_PREPARING":
            [Pitching,Yawing,Heave,Surge]=self.PreparingMode(SensData)
        
        # Readyの処理
        if CNTRLMODE=="FULLAUTO_READY":
            # ステートだけ変更動作内容はPreparingと全く同じ
            [Pitching,Yawing,Heave,Surge]=self.PreparingMode(SensData)

        # Serch時の処理
        if CNTRLMODE=="SERCH_READY":
            return
        
        # Approach時の処理
        

        input_th_all=[self.input_th1,self.input_th2,self.input_th3,self.input_th4]
        input_srv_all=[self.input_srv1,self.input_srv2]
        input_chu_all=[self.input_chu1,self.input_chu2]



        return [*input_th_all,*input_srv_all,*input_chu_all],CNTRLMODE
    

    def Chck_UnedrWater(self,Dep,Dist):
        # 水中かチェック
        # 深度センサの値が??まで大きい AND 超音波センサの値が0より大きい　 
        if Dep>=self.dep_underwater and Dist>0:
            self.UnderWaterFlg=True
        else:
            self.UnderWaterFlg=False
    
    def StateMachine(self,SensData,CameraData,CNTRLMODE):
        # AutoControlの場合はパススルー
        if CNTRLMODE=="AUTO_CONTROL":
            return "AUTO_CONTROL"
        
        # 水中か確認
        self.Chck_UnedrWater(SensData[9],SensData[10])
        # 水中じゃなかったら問答無用でPreparingに移行
        if self.UnderWaterFlg==False:
            return "FULLAUTO_PREPARING"
        
        # Preparing→Ready
        if CNTRLMODE=="FULLAUTO_PREPARING":
            # ベース深度とセンサ深度の誤差が0.1以内に3s間いれば次のステートに移行する。
            if abs(SensData[9]-self.dep_base)<=0.1:
                self.dep_reach_num+=1
            if self.dep_reach_num>=300:
                return "FULLAUTO_READY"
        
        # Ready→Serch
        if CNTRLMODE=="FULLAUTO_READY":
            # カメラからのデータがemptyじゃなければ次のステートに移行する。
            if len(CameraData)>=0:
                return "SEARCH"
        
        # Serch→Approach
            


    def PreparingMode(self,SensData):
        Dep=SensData[9]
        if self.UnderWaterFlg:
            # 水中に入ってたらベースまで深度を下げる
            Pitching=0
            Yawing=0
            Heave=self.HEAVE.Control(self.dep_base,Dep,self.KpDep,self.KiDep,self.KdDep)
            Surge=0
        else:
            Pitching=0
            Yawing=0
            Heave=0
            Surge=0
        return [Pitching,Yawing,Heave,Surge]
    
    def SearchMode(self,SensData,CameraData):
        return
    
    def ApproachMode(self,SensData,CameraData):
        return
    
    
    


    
    def setPIDgain(self,PIDgain):
        self.KpDep=PIDgain[0]
        self.KpPitch=PIDgain[1]
        self.KpYaw=PIDgain[2]
        self.KiDep=PIDgain[3]
        self.KiPitch=PIDgain[4]
        self.KiYaw=PIDgain[5]
        self.KdDep=PIDgain[6]
        self.KdPitch=PIDgain[7]
        self.KdYaw=PIDgain[8]
            
            




    

        
    # SensData→[gx,gy,gz,ax,ay,az,roll,pitch,yaw,dep,dist]
    # CNTRLMODE→np.numpy
    # CameraData→[mx_norma,my_norma,s]
    def Controller(self,PropoData,SensData,PIDGain,CameraData,CNTRLMODE):
        print(len(CameraData))
        self.setPIDgain(PIDGain)
        # マニュアルコントロールが選択
        if CNTRLMODE==self.SA.Encode_OneSignal("STCONTROLLER","MANUAL_CONTROL"):
            return self.ManualController(PropoData),CNTRLMODE
        # Attitudeコントロールが選択
        elif CNTRLMODE==self.SA.Encode_OneSignal("STCONTROLLER","ATTITUDE_CONTROL"):
            return self.Attitude_PIDController(self.ReferenceGenerator_fromPropo(PropoData),SensData),CNTRLMODE
        # フルオートモード移行
        elif CNTRLMODE>=self.SA.Encode_OneSignal("STCONTROLLER","AUTO_CONTROL"):
            return self.FullAuto_Controller(SensData,CameraData,self.SA.Decode_OneSignal("STCONTROLLER",int(CNTRLMODE)))
        else :
            print("use valid controll mode")
            return [1600,1600,1600,1600,0.0,0.0,0.0,0.0]

class PID:
    def __init__(self,Ts):
        self.Ts=Ts #[s]で入力
        self.integ=0.0
        self.e_old=0.0
    
    def IntegInit(self):
        self.integ=0.0
        self.e_old=0.0
    
    def Control(self,Ref,Sens,Kp,Ki,Kd):
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

        return (P_out+I_out+D_out+I_out)