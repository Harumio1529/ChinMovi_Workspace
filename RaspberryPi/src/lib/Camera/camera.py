import cv2
import numpy as np


class camera():
    def __init__(self,DEBUG_PRINT):
        self.LOW_COLOR1 = np.array([0, 50, 50]) # 各最小値を指定
        self.HIGH_COLOR1 = np.array([6, 255, 255]) # 各最大値を指定
        self.LOW_COLOR2 = np.array([174, 50, 50])
        self.HIGH_COLOR2 = np.array([180, 255, 255])
        self.DP=DEBUG_PRINT
    
    def debugprint(self,data):
        if self.DP:
            print(data)

    def Clahe(self,img):

        img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV) # RGB => YUV(YCbCr)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)) # claheオブジェクトを生成
        img_yuv[:,:,0] = clahe.apply(img_yuv[:,:,0]) # 輝度にのみヒストグラム平坦化
        img = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR) # YUV => RGB

        img_blur = cv2.blur(img, (15, 15)) 

        hsv = cv2.cvtColor(img_blur, cv2.COLOR_BGR2HSV) # BGRからHSVに変換

        bin_img1 = cv2.inRange(hsv, self.LOW_COLOR1, self.HIGH_COLOR1) # マスクを作成
        bin_img2 = cv2.inRange(hsv, self.LOW_COLOR2, self.HIGH_COLOR2)
        mask = bin_img1 + bin_img2 # マスクの足し合わせ。赤は色相でいうと0-360にかかるので領域を分けている。
        masked_img = cv2.bitwise_and(img, img, mask= mask) # 元画像にマスクをかぶせる

        num_labels,label_img,status,centroids=cv2.connectedComponentsWithStats(mask) #マスクの情報を取得

        num_labels = num_labels - 1
        status = np.delete(status, 0, 0)
        centroids = np.delete(centroids, 0, 0)

        for index in range(num_labels):
            x=status[index][0] # x:バウンディングボックスの左上X座標
            y=status[index][1] # y:バウンディングボックスの左上Y座標
            w=status[index][2] # w:バウンディングボックスの幅
            h=status[index][3] # h:バウンディングボックスの高さ
            s=status[index][4] # s:バウンディングボックスの面積
            mx=int(centroids[index][0]) # mx:バウンディングボックスの重心の座標
            my=int(centroids[index][1]) # my:バウンディングボックスの重心の座標

            # 面積が一定以上の赤をバウンディングボックスで囲む
            if s>300 :
                # cv2.rectangle(masked_img,(x,y),(x+w,y+h),(255,0,255))
                # cv2.circle(masked_img,(mx,my),5,(255,255,0))
                # cv2.putText(masked_img, "%d"%s, (x-15, y+h+15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,255))
                cv2.circle(img,(mx,my),5,(255,255,0))
                cv2.putText(img, "%d"%s, (x-15, y+h+15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))

        # return masked_img
        return img
    
    



def main():
    cap = cv2.VideoCapture(0)
    CM=camera()

    while True:
        ret, low = cap.read()
        h,w,c=low.shape
        print(h)
        print(w)
        frame=CM.Clahe(low)
        cv2.imshow('image', frame)
        # cv2.imshow('image', low)

        key = cv2.waitKey(1)
        if key == ord('q'):  # qキーで終了
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__=="__main__":
    main()
