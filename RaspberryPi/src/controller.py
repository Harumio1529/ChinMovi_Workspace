import time
import numpy as np

# コントローラ計算
class Controller():
    def __init__(self,SA):
        # statusanalyzer
        self.SA=SA
        self.AREA_MEMORY = []
        self.Area_tol = 1e-3
        self.ApproachDist = 1e-2
        self.AttackDist = 200 # mm

        self.CurrentMeanArea=0
        self.max_AREA=0

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

    # サーボはcloseがTrue
    # 注射器はずっとFalse
    def FullAuto_Controller(self,SensData,CameraData,CNTRLMODE):
        # 水中か確認
        self.Chck_UnedrWater(SensData[9],SensData[10])
        # 水中じゃなかったら問答無用でPreparingに移行
        if self.UnderWaterFlg==False:
            CNTRLMODE="FULLAUTO_PREPARING"

        # AutoControlの時の処理
        if CNTRLMODE=="AUTO_CONTROL":
            [Pitching,Yawing,Heave,Surge],Servo,Chusyaki=[0.0,0.0,0.0,0.0],True,False

        
        # Preparingの時の処理
        if CNTRLMODE=="FULLAUTO_PREPARING":
            [Pitching,Yawing,Heave,Surge],Servo,Chusyaki=self.PreparingMode(SensData)
            # ベース深度とセンサ深度の誤差が0.1以内に3s間いれば次のステートに移行する。
            if abs(SensData[9]-self.dep_base)<=0.1:
                self.dep_reach_num+=1
            if self.dep_reach_num>=300:
                CNTRLMODE="FULLAUTO_READY"
        
        # Readyの処理
        if CNTRLMODE=="FULLAUTO_READY":
            # ステートだけ変更動作内容はPreparingと全く同じ
            [Pitching,Yawing,Heave,Surge],Servo,Chusyaki=self.PreparingMode(SensData)
            # カメラからのデータがemptyじゃなければ次のステートに移行する。
            if len(CameraData)>=0:
                CNTRLMODE="SEARCH"

        # Serch時の処理
        if CNTRLMODE=="SEARCH":
            # serch_time 秒間探索する
            self.serch_time = 6
            self.serch_counter+=1
            if self.serch_counter<=int(self.serch_time*100):
            # 回りながら探索
                [Pitching,Yawing,Heave,Surge],Servo,Chusyaki=self.SearchMode(SensData)
            else:
                CNTRLMODE = "DETERMIN"
                [Pitching,Yawing,Heave,Surge],Servo,Chusyaki=[0.0,0.0,0.0,0.0],True,False
        
        # DETERMINの時の処理
        if CNTRLMODE=="DETERMIN":
            if abs(self.CurrentMeanArea - self.max_AREA) < self.max_AREA*self.Area_tol:
                [Pitching,Yawing,Heave,Surge],Servo,Chusyaki=[0.0,0.0,0.0,0.0],True,False
                CNTRLMODE="APPROACH"
            else:
                [Pitching,Yawing,Heave,Surge],Servo,Chusyaki=self.Determin(SensData)
            


        # ランダムヲーク時の処理
        if CNTRLMODE=="RANDOM_WALK":
            return
        
        if CNTRLMODE=="HEADING_ADJUST":
            [Pitching,Yawing,Heave,Surge],Servo,Chusyaki=self.Heading_adjust(SensData)


        # 接近モード時の処理
        if CNTRLMODE=="APPROACH":
            [Pitching,Yawing,Heave,Surge],Servo,Chusyaki=self.Approach(SensData)
        
        # 割るモード時の処理
        if CNTRLMODE=="ATTACK":
            return

        # 悪モード the beast時の処理
        if CNTRLMODE=="ATTACK_BEAST":
            return

        # 他の風船に行く時の処理
        if CNTRLMODE=="TARGET_CHANGE":
            # serch_time 秒間探索する
            self.TARGET_CNG_bkwd_timing = 1 # 1sec
            self.TARGET_CNG_turn_timing = 2
            self.TARGET_CNG_fwd_timing = 3
            self.TARGET_CNG_counter += 1

            if self.TARGET_CNG_counter <= int(self.TARGET_CNG_bkwd_timing*100): #0~1secの時
                #微速で1秒後ずさりする
                [Pitching,Yawing,Heave,Surge]=self.TargetCngMode(0)
            elif (self.TARGET_CNG_counter > int((self.TARGET_CNG_bkwd_timing)*100)) and (self.TARGET_CNG_counter <= int(self.TARGET_CNG_turn_timing*100)): #1~2secの時
                #1秒回頭する (約60deg分)
                [Pitching,Yawing,Heave,Surge]=self.TargetCngMode(1)
            elif (self.TARGET_CNG_counter > int((self.TARGET_CNG_turn_timing)*100)) and (self.TARGET_CNG_counter <= int(self.TARGET_CNG_fwd_timing*100)): #2~3secの時
                #微速で前進する
                [Pitching,Yawing,Heave,Surge]=self.TargetCngMode(2)
            else:
                #SEARCH MODEへ
                CNTRLMODE = "SEARCH"
                [Pitching,Yawing,Heave,Surge]=[0.0,0.0,0.0,0.0]
            return [Pitching,Yawing,Heave,Surge],False,False
        
        # ミキサー
        self.input_th1=int(-600*(Surge+Yawing)+1600)
        self.input_th2=int(600*(Surge-Yawing)+1600)
        self.input_th3=int(600*(Pitching+Heave)+1600)
        self.input_th4=int(600*(-Pitching+Heave)+1600)
        input_th_all=[self.input_th1,self.input_th2,self.input_th3,self.input_th4]
        # アーム
        if Servo:
            # Trueで閉じる
            self.input_srv1=2800  #値大で閉じる
            self.input_srv2=600   #値小で閉じる
        else:
            # Falseで開く
            self.input_srv1=1300
            self.input_srv2=2100
        input_srv_all=[self.input_srv1,self.input_srv2]
            
        # 注射器
        self.input_chu1=0
        self.input_chu2=0
        input_chu_all=[self.input_chu1,self.input_chu2]
        
        return [*input_th_all,*input_srv_all,*input_chu_all],CNTRLMODE
    

    def Chck_UnedrWater(self,Dep,Dist):
        # 水中かチェック
        # 深度センサの値が??まで大きい AND 超音波センサの値が0より大きい　 
        if Dep>=self.dep_underwater and Dist>0:
            self.UnderWaterFlg=True
        else:
            self.UnderWaterFlg=False
    

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
        return [Pitching,Yawing,Heave,Surge],True,False
    
    def SearchMode(self,SensData,CameraData):
        Current_AREA = CameraData[2]
        self.AREA_MEMORY.append(Current_AREA)
        return [0.0,1.0,0.0,0.0],True,False
    
    def Determin(self,SensData,CameraData):
        # mean_num個の移動平均
        mean_num = 60
        data = np.array(self.AREA_MEMORY, dtype=float)
        avgs = np.convolve(data, np.ones(mean_num)/mean_num, mode="valid")
        self.max_AREA = np.max(avgs)
        self.AREA_MEMORY.clear()

        # 目標に照準を合わせる
        Current_AREA = CameraData[2]
        self.AREA_MEMORY.append(Current_AREA)
        self.area_values = np.array(self.AREA_MEMORY, dtype=float)
        self.last_values = self.area_values[-30:]
        self.CurrentMeanArea = np.mean(self.last_values) if self.last_values.size > 0 else None
        return [0.0,1.0,0.0,0.0],True,False
    
    def Heading_adjust(self,SensData,CameraData):
        self.ObjectX = self.CameraData[0]
        self.ObjectY = self.CameraData[1]
        self.TargetX = 0.
        self.TargetY = 0.
        # TargetXが0に近づくようにYawを調整
        self.errX = (self.ObjectX - self.TargetX)
        self.Yawing = self.errX
        # TargetYが0に近づくようにHeaveを調整
        self.errY = (self.ObjectY - self.TargetY)
        self.Heave = self.errY
        # 誤差が閾値以下になればAPPROACH移行する
        if abs(self.errX)+abs(self.errY) < self.ApproachDist:
            self.CNTRLMODE = "APPROACH"
        return [0.,self.Yawing,self.Heave,0.],Servo,Chusyaki
    
    def Approach(self,SensData,CameraData):
        Surge = 1.
        self.ObjectX = self.CameraData[0]
        self.ObjectY = self.CameraData[1]
        self.TargetX = 0.
        self.TargetY = 0.
        # TargetXが0に近づくようにYawを調整
        self.errX = (self.ObjectX - self.TargetX)
        self.Yawing = self.errX
        # TargetYが0に近づくようにHeaveを調整
        self.errY = (self.ObjectY - self.TargetY)
        self.Heave = self.errY
        # 誤差が閾値以下になればAPPROACH移行する
        self.SS_Distance = SensData[10]
        if self.SS_Distance < self.AttackDist:
            self.CNTRLMODE = "APPROACH"
            self.Yawing = 0.
            self.Heave = 0.
        return [0.,self.Yawing,self.Heave,0.],Servo,Chusyaki
    
    def AttackMode(self,SensData,CameraData):
        return [Pitching,Yawing,Heave,Surge],Servo,Chusyaki

    def TargetCngMode(self,phase):
        if phase = 0: #後ずさり
            return [0.,0.,0.,-0.3]
        elif phase = 1: #回頭
            return [0.,1.,0.,0.]
        elif phase = 2: #微速前進
            return [0.,0.,0.,0.3]
        else: 
            return [0.,0.,0.,0.]
        
    
    
    


    
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