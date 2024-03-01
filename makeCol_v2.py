import numpy as np
from cv2 import cv2
import random
import boto3

# 水着のマスク画像作成
def swimsuit(src):
 
    hsv = cv2.cvtColor(src, cv2.COLOR_BGR2HSV)
    # 取得する色の範囲を指定する
    lower = np.array([  0,180, 8])
    upper = np.array([255,255,247])
 
    # 指定した色に基づいたマスク画像の生成
    swimsuit_mask = cv2.inRange(hsv, lower, upper)
    cv2.imwrite('swimsuit_mask.jpg',swimsuit_mask)
    return swimsuit_mask

# 水着輪郭検知
def contour_detection(swimsuit_bw, src):
 
    # 輪郭を抽出
    contours,hierarchy = cv2.findContours(swimsuit_bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #contours.sort(key=cv2.contourArea, reverse=True)
    i = 1
    swimrect_arr = [[0,0,0,0]]
    for contour in contours:
           # 凸包の取得
        approx = cv2.convexHull(contour)
           # 輪郭の領域を計算
        area = cv2.contourArea(approx)
        # ノイズ除外
        if area < 1e1:
           continue
        swimsuit_rect = cv2.boundingRect(contour)   
        swimrect_arr = np.append(swimrect_arr,np.array([[swimsuit_rect[0],swimsuit_rect[1],swimsuit_rect[2],swimsuit_rect[3]]]),axis=0) 
        x,y,w,h = cv2.boundingRect(contour)
        cv2.rectangle(src,(x,y),(x+w,y+h),(0,255,0),2)
    return swimrect_arr 

#水着輪郭衝突判定
def swimsuit_collision(swimrect_arr,mizutama_x,mizutama_y,mizutama_r):
    #衝突判定
    for i in range(len(swimrect_arr)-1):
        #print('index')
        rect_cx = swimrect_arr[i+1][0] + swimrect_arr[i+1][2]/2
        rect_cy = swimrect_arr[i+1][1] + swimrect_arr[i+1][3]/2
        dist_c = np.sqrt((mizutama_x - rect_cx) ** 2 + (mizutama_y - rect_cy) ** 2) 
        rect_r = np.sqrt((swimrect_arr[i+1][2]/2) ** 2 + (swimrect_arr[i+1][3]/2) ** 2)
        dist_r = rect_r + mizutama_r
        if dist_r > dist_c:
            return False
    return True
               
#肌のマスク画像を作成
def create_skin_mask(src):
    hsv = cv2.cvtColor(src,cv2.COLOR_BGR2HSV)
    lower = np.array([0,60,80])
    upper = np.array([30,255,255])
    skin_mask = cv2.inRange(hsv,lower,upper)
    cv2.imwrite('skin_mask.jpg',skin_mask)
    return skin_mask

#肌マスク画像から水玉の中心座標を取得
def getSkinMizutamPoint(src,skin_mask):
    maskHeight, maskWidth =  src.shape[:2]
    while True:
        circle_x = random.randrange(6,maskWidth - 6)
        circle_y = random.randrange(6,maskHeight - 6)
        val = skin_mask[circle_y,circle_x]
        if val == 255:
            break
        else:
            pass    
    return circle_x, circle_y

#顔検出
def faceDetect(src):
    cascade_path = './cv2/data/haarcascade_frontalface_default.xml'
    cascade  = cv2.CascadeClassifier(cascade_path)
    img_gray  = cv2.cvtColor(src,cv2.COLOR_BGR2GRAY)
    facerect  = cascade.detectMultiScale(img_gray, scaleFactor=1.11, minNeighbors=1, minSize=(80, 80))
    return facerect


#顔の水玉を抽出
def faceMizutamaDedide(facerect,color_mask, src,mask):
    if len(facerect) > 0:
        rect = facerect[0]
        face_x = rect[0] + int(rect[2]/2)
        face_y = rect[1] + int(rect[3]/2)
        face_r = rect[3]
        cv2.circle(src,(face_x,face_y),face_r,color_mask,3)
        cv2.circle(mask,(face_x,face_y),face_r,color_mask,-1)
        mizutama_arr =  [[face_x,face_y,face_r]]
    else:
        mizutama_arr = [[0,0,0]]
        face_r = 0
    return mizutama_arr, face_r

#水玉の位置を決定する
def makeMizutamaPos(mizutama_arr,facerect,src,skin_mask, mask,swimsuit_rect_arr,face_r):
    mizutama_cnt = 0
    roop_cnt = 0
    if len(facerect) > 0:
        while mizutama_cnt < 10:
            print(roop_cnt)
            if roop_cnt > 150000:
                break
            mizutama_x,mizutama_y = getSkinMizutamPoint(src,skin_mask)
            mizutama_r = random.randrange(int(face_r * 0.25),int(face_r * 1.2))
            for i in range(len(mizutama_arr)):
                c_dest = np.sqrt((mizutama_x - mizutama_arr[i-1][0]) ** 2 + (mizutama_y - mizutama_arr[i-1][1]) ** 2) 
                r_dest = mizutama_r + mizutama_arr[i-1][2]
                if c_dest > r_dest:
                    pass
                else:
                    roop_cnt += 1
                    break 
                if i == len(mizutama_arr)-1:
                    swimsuit_flg = swimsuit_collision(swimsuit_rect_arr,mizutama_x,mizutama_y,mizutama_r)
                    if swimsuit_flg:
                        mizutama_arr = np.append(mizutama_arr,np.array([[mizutama_x,mizutama_y,mizutama_r]]),axis=0)    
                        cv2.circle(src,(mizutama_x,mizutama_y),mizutama_r,color,3)
                        cv2.circle(mask,(mizutama_x,mizutama_y),mizutama_r,color_mask,-1)
                        mizutama_cnt += 1
                        print('index')
                        print(mizutama_cnt)
                        roop_cnt += 1
                    else:
                        roop_cnt += 1
                        break
        return '水玉こら作成完了',True
    else:
        return 'グラビア画像として認識できません',False    
#####################################################
color = (255, 0, 0) 
color1 = (0, 0, 255) 
color_mask = (255, 255, 255) 


#メイン処理

#画像読込・初期処理
###################################
def makeImage(srcName):
    #srcName = 'testpy.jpg'
    src = cv2.imread(srcName)
    origin = cv2.imread(srcName)
    mask = cv2.imread(srcName)
    height, width = mask.shape[:2]
    pts = np.array( [ [0,0], [0,height], [width, height], [width,0] ] )
    mask = cv2.fillPoly(mask, pts =[pts],color=(0,0,0))
    cv2.imwrite('mask.jpg', mask)
    ####################################

    #肌マスク作成
    skin_mask = create_skin_mask(src)

    #水着マスク作成
    swimsuit_mask = swimsuit(src)

    #水着輪郭抽出
    swimsuit_rect_arr = contour_detection(swimsuit_mask,src)

    #顔検出
    facerect  = faceDetect(src)

    #顔水玉位置決定
    mizutama_arr,face_r = faceMizutamaDedide(facerect,color_mask,src,mask)

    #そのほか水玉位置決定
    msg,completeFlg = makeMizutamaPos(mizutama_arr,facerect,src,skin_mask,mask,swimsuit_rect_arr,face_r)

    #画像保存処理
    #######################################
    mask_gray  = cv2.cvtColor(mask,cv2.COLOR_BGR2GRAY)
    masked = cv2.bitwise_and(origin, origin, mask=mask_gray)
    cv2.imwrite('face_detect.jpg',src)
    cv2.imwrite('mask_result.jpg',mask)
    cv2.imwrite('masked_result.jpg',masked)
    #S3アクセス＆アップロード
    accesskey = "AKIARWVS365LHIQP6E4O"
    secretkey = "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"
    region = "ap-northeast-1"
    s3 = boto3.client('s3', aws_access_key_id=accesskey, aws_secret_access_key= secretkey, region_name=region)
    filename = "masked_result.jpg"
    bucket_name = "accept-image"
    s3.upload_file(filename,bucket_name,filename,ExtraArgs={"ContentType": "./", 'ACL':'public-read'})

    #bucket = s3.Bucket('accept-image')
    #bucket.upload_file('masked_result.jpg','https://s3-ap-northeast-1.amazonaws.com/accept-image')
    print('水玉配列')
    print(mizutama_arr)
    print(msg)
    return msg,completeFlg
    #######################################