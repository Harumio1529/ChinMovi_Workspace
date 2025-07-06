import cv2
import numpy as np

LOW_COLOR1 = np.array([0, 50, 50]) # 各最小値を指定
HIGH_COLOR1 = np.array([6, 255, 255]) # 各最大値を指定
LOW_COLOR2 = np.array([174, 50, 50])
HIGH_COLOR2 = np.array([180, 255, 255])

def Clahe(img):
    # img = cv2.imread(image_low) # 画像を読み込む

    img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV) # RGB => YUV(YCbCr)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8)) # claheオブジェクトを生成
    img_yuv[:,:,0] = clahe.apply(img_yuv[:,:,0]) # 輝度にのみヒストグラム平坦化
    img = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR) # YUV => RGB

    img_blur = cv2.blur(img, (15, 15)) 

    hsv = cv2.cvtColor(img_blur, cv2.COLOR_BGR2HSV) # BGRからHSVに変換

    bin_img1 = cv2.inRange(hsv, LOW_COLOR1, HIGH_COLOR1) # マスクを作成
    bin_img2 = cv2.inRange(hsv, LOW_COLOR2, HIGH_COLOR2)
    mask = bin_img1 + bin_img2 # 必要ならマスクを足し合わせる
    masked_img = cv2.bitwise_and(img, img, mask= mask) # 元画像から特定の色を抽出

    num_labels,label_img,status,centroids=cv2.connectedComponentsWithStats(mask)

    num_labels = num_labels - 1
    status = np.delete(status, 0, 0)
    centroids = np.delete(centroids, 0, 0)

    for index in range(num_labels):
        x=status[index][0]
        y=status[index][1]
        w=status[index][2]
        h=status[index][3]
        s=status[index][4]
        mx=int(centroids[index][0])
        my=int(centroids[index][1])

        if s>300 :
            # cv2.rectangle(masked_img,(x,y),(x+w,y+h),(255,0,255))
            # cv2.circle(masked_img,(mx,my),5,(255,255,0))
            # cv2.putText(masked_img, "%d"%s, (x-15, y+h+15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,255))
            cv2.circle(img,(mx,my),5,(255,255,0))
            cv2.putText(img, "%d"%s, (x-15, y+h+15), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0))

    # return masked_img
    return img


cap = cv2.VideoCapture(0)

while True:
    ret, low = cap.read()
    frame=Clahe(low)
    # print(type(frame))
    # print(frame.nbytes)
    # print(frame.itemsize)
    # print(frame.size)
    cv2.imshow('image', frame)
    # cv2.imshow('image', low)

    key = cv2.waitKey(1)
    if key == ord('q'):  # qキーで終了
        break
    


cap.release()
cv2.destroyAllWindows()
