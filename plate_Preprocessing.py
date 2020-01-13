import cv2

import dlib

import numpy as np

import math
from skew_detection import *
import os
import shutil
class Preprocessing:
    def __init__(self):
        self.a = 0
    def brightness(self, img ): #計算亮度
        cols, rows ,a= img.shape
        brightness = np.sum(img) / (255 * cols * rows)
        print(brightness)
        return brightness

    
    def lightProcessing(self,img):#調整亮度
        minimum_brightness = 1.5 #閥值
        brightness = self.brightness(img)
        ratio  = brightness/minimum_brightness
        r = cv2.convertScaleAbs(img, alpha = 1 / ratio , beta = 0)
        return r
    
    def hisEqulColor(self,img): #直方距離放大
        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
        channels = cv2.split(ycrcb)
        equ = cv2.equalizeHist(channels[0], channels[0])
        equ = cv2.merge(channels, ycrcb)
        equ = cv2.cvtColor(ycrcb, cv2.COLOR_YCR_CB2BGR)
        return equ

    def rotImg(self,img):
        
#        print('Original Dimensions : ',img.shape)
#        scale_percent = 1000 # percent of original size
#        width = int(img.shape[1] * scale_percent / 100)
#        height = int(img.shape[0] * scale_percent / 100)
#        dim = (width, height)
#        
#        gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#        
#        sift = cv2.xfeatures2d.SIFT_create(nfeatures = 400,
#                                            nOctaveLayers = 100,
#                                            contrastThreshold = 0.04,
#                                            edgeThreshold = 10,
#                                            sigma = 1.6 )
#        
#        kp, des = sift.detectAndCompute(gray,None)
#        kp, des = sift.compute(gray,kp)
#        h = img.shape[0]
#        w = img.shape[1]
#        good = []
#        a = c = 0
#        b = d = w
#        ap = bp = cp = dp = ()
#        def tack(k):
#            return k.pt[1]
#        kp.sort(key=tack)
#        
#        for i in kp:
#            print(i.pt[0])
#            if (i.pt[1] < h * 0.3 and i.pt[0] > w *0.2):
#                #good.append(i)
#                if i.pt[0] > a:
#                    a = i.pt[0]
#                    ap = i
#                if i.pt[0] < b:
#                    b = i.pt[0]
#                    bp = i
#            if (i.pt[1] > h * 0.8 and i.pt[0] > w *0.2):
#                if i.pt[0] > c :
#                    c = i.pt[0]
#                    cp = i
#                if i.pt[0] < d:
#                    d = i.pt[0]
#                    dp = i
#        
#        good.append(ap)
#        good.append(bp)
#        good.append(cp)
#        good.append(dp)
#        
#        x1 = int(ap.pt[0])
#        y1 = int(ap.pt[1])
#        x2 = int(bp.pt[0])
#        y2 = int(bp.pt[1])
#        
#        tx = (x2 - x1)
#        ty = (y2 - y1)
#        m = ty / tx
#        b = y1-(m*x1)
#        y3 = m * 0 + b
#        y4 = m * w + b
#        
#        x1 = int(cp.pt[0])
#        y1 = int(cp.pt[1])
#        x2 = int(dp.pt[0])
#        y2 = int(dp.pt[1])
#        
#        tx = (x2 - x1)
#        ty = (y2 - y1)
#        m = ty / tx
#        b = y1-(m*x1)
#        y5 = m * 0 + b
#        y6 = m * w + b
#        
#        cv2.line(gray,(int(0), int(y3)),(int(w), int(y4)),(0,0,255),1)
#        cv2.line(gray,(int(ap.pt[0]), int(ap.pt[1])),(int(bp.pt[0]), int(bp.pt[1])),(0,0,255),1)
#        #cv2.line(gray,(int(cp.pt[0]), int(cp.pt[1])),(int(dp.pt[0]), int(dp.pt[1])),(0,0,255),1)
#        
#        print('(%f, %f), (%f, %f), (%f, %f)'%(ap.pt[0], ap.pt[1], bp.pt[0], bp.pt[1], b, a))
#        
#        pts1 = np.float32([[0 ,y3],[w , y4],[0 , y5], [w , y6]])
#        pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
#        M = cv2.getPerspectiveTransform(pts1,pts2)
#        dst = cv2.warpPerspective(img,M,(img.shape[1], img.shape[0]))
#        #cv2.imwrite('turn.jpg',dst)
#        img=cv2.drawKeypoints(gray, good, outImage = None, color=(255,0,0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
#        #cv2.imwrite('sift_keypoints.jpg',img)
#        return dst
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        skew_h, skew_v = skew_detection(gray)
        corr_img = v_rot(img, (90 - skew_v + skew_h), img.shape, 30);
        corr_img = h_rot(corr_img, skew_h)
        return corr_img
#        img = cv2.imread(r'C:\Users\tiger\Downloads\main6\61-0.jpg', cv2.IMREAD_UNCHANGED)
#        print('Original Dimensions : ',img.shape)
#        img = self.hisEqulColor(img)
#        scale_percent = 1000 # percent of original size
#        width = int(img.shape[1] * 2)
#        height = int(img.shape[0] * 2)
#        dim = (width, height)
#        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
#        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#        #gray = cv2.GaussianBlur(gray, (3, 3), 0)
#        
#        # 畫線:
#        FilterSize = 3
#        v = np.median(img)
#        sigma=0.55
#        # 选择合适的lower和upper值，然后应用它们
#        lower = int(max(0, (1.0 - sigma) * v))
#        upper = int(min(255, (1.0 + sigma) * v))
#        edges = cv2.Canny(gray, lower, upper, FilterSize)
#        lines = cv2.HoughLinesP(edges ,rho = 1,theta = 1*np.pi/180,threshold = 80,minLineLength = 80,maxLineGap = 30)
#        tx1 = ty1 = tx3 = ty3 = img.shape[1]
#        tx2 = ty2 = tx4 = ty4 = 0
#        
#        for i in range(len(lines)):
#            x1 = lines[i][0][0]
#            y1 = lines[i][0][1]    
#            x2 = lines[i][0][2]
#            y2 = lines[i][0][3]
#            if ((y1 < img.shape[0]*0.3 or y1 > img.shape[0]*0.7) and (y2 < img.shape[0]*0.3 or y2 > img.shape[0]*0.7)):
#                if(y1 < img.shape[0]*0.3):
#                    if(tx1 > x1 or ty1 > y1):
#                        tx1 = x1
#                        ty1 = y1
#                    if(tx2 < x2 or ty2 < y2):
#                        tx2 = x2
#                        ty2 = y2   
#                if(y1 > img.shape[0]*0.7):
#                    if(tx3 > x1 or ty3 > y1):
#                        tx3 = x1
#                        ty3 = y1
#                    if(tx4 < x2 or ty4 < y2):
#                        tx4 = x2
#                        ty4 = y2      
#                #cv2.line(img,(x1,y1),(x2,y2),(0,0,255),1)
#        print(tx1 ,ty1 , tx2 , ty2 , tx3 , ty3 , tx4 , ty4)
#        #轉正
#        print(img.shape[0], img.shape[1])
#        pts1 = np.float32([[0 ,ty1],[img.shape[1] , ty2],[0 , ty3], [img.shape[1] , ty4]])
#        pts2 = np.float32([[0, 0], [img.shape[1], 0], [0, img.shape[0]], [img.shape[1], img.shape[0]]])
#        M = cv2.getPerspectiveTransform(pts1,pts2)
#        dst = cv2.warpPerspective(img,M,(img.shape[1], img.shape[0]))
##        print(type(dst))
##        cv2.imshow("1",dst)
##        cv2.waitKey(1)
#        return dst


#p = Preprocessing()
#input_path = r"G:\YOLO_plate\pro"#資料夾目錄
#output_path = r"G:\YOLO_plate\plate\light_pro\train"
#files= os.listdir(input_path) #得到資料夾下的所有檔名稱
#s = []
#for file in files: #遍歷資料夾
#    print(file)
#    if not os.path.isdir(file): #判斷是否是資料夾,不是資料夾才打開
#        if ".jpg" in file:
#            f = cv2.imread(input_path+"\\"+file)
#            #f=cv2.imdecode(np.fromfile(input_path+"\\"+file,dtype=np.uint8),-1)
#            print(file)
#            img = p.lightProcessing(f)
#            cv2.imwrite(output_path+"\\"+file, img)
#        else:
#            shutil.copy(input_path+'\\'+file,output_path+'\\'+file)

