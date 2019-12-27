# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 23:45:11 2019

@author: harry
"""

import os
import cv2
import darknet


class YOLO:
    def __init__(self,configPath="./cfg/yolov3-tiny-face.cfg",weightPath="./weights/yolov3-tiny-face_55000.weights",metaPath="./cfg/obj.data"):
        self.netMain = None
        self.metaMain = None
        self.altNames = None
        self.configPath = configPath
        self.weightPath = weightPath
        self.metaPath = metaPath
        self.darknet_image = None
        self.yolo_init()
        self.resize_img = None
        
    def yolo_init(self):
        if not os.path.exists(self.configPath):
            raise ValueError("Invalid config path `" +
                             os.path.abspath(self.configPath)+"`")
        if not os.path.exists(self.weightPath):
            raise ValueError("Invalid weight path `" +
                             os.path.abspath(self.weightPath)+"`")
        if not os.path.exists(self.metaPath):
            raise ValueError("Invalid data file path `" +
                             os.path.abspath(self.metaPath)+"`")
        if self.netMain is None:
            self.netMain = darknet.load_net_custom(self.configPath.encode(
                "ascii"), self.weightPath.encode("ascii"), 0, 1)  # batch size = 1
        if self.metaMain is None:
            self.metaMain = darknet.load_meta(self.metaPath.encode("ascii"))
        if self.altNames is None:
            try:
                with open(self.metaPath) as metaFH:
                    metaContents = metaFH.read()
                    import re
                    match = re.search("names *= *(.*)$", metaContents,
                                      re.IGNORECASE | re.MULTILINE)
                    if match:
                        result = match.group(1)
                    else:
                        result = None
                    try:
                        if os.path.exists(result):
                            with open(result) as namesFH:
                                namesList = namesFH.read().strip().split("\n")
                                self.altNames = [x.strip() for x in namesList]
                    except TypeError:
                        pass
            except Exception:
                pass
            
        print("Starting the YOLO loop...")
    
        # Create an image we reuse for each detect
        self.darknet_image = darknet.make_image(darknet.network_width(self.netMain),
                                        darknet.network_height(self.netMain),3)
        
    def convertBack(self,x, y, w, h,plt1,plt2):
        xmin = int(round(x - (w / 2))*(plt1[0]/plt2[0]))
        xmax = int(round(x + (w / 2))*(plt1[0]/plt2[0]))
        ymin = int(round(y - (h / 2))*(plt1[1]/plt2[1]))
        ymax = int(round(y + (h / 2))*(plt1[1]/plt2[1]))
        
        return xmin, ymin, xmax, ymax
    def convertBack_resize(self,x, y, w, h):
        xmin = int(round(x - (w / 2)))
        xmax = int(round(x + (w / 2)))
        ymin = int(round(y - (h / 2)))
        ymax = int(round(y + (h / 2)))
        
        return xmin, ymin, xmax, ymax

    def cut_image(self,detections,img):
        
        obj_img = []
        expand_x = 10
        expand_y = 10
        
        for detection in detections:
            x, y, w, h = detection[2][0],\
                detection[2][1],\
                detection[2][2],\
                detection[2][3]
            xmin, ymin, xmax, ymax = self.convertBack(
                float(x), float(y), float(w), float(h),[img.shape[1],img.shape[0]],[self.resize_img.shape[1],self.resize_img.shape[0]])
            
            pt1 = (xmin-expand_x, ymin-expand_y)
            pt2 = (xmax+expand_x, ymax+expand_y)
            
            xmin = pt1[0] if pt1[0] > 0 else 0
            ymin = pt1[1] if pt1[1] > 0 else 0
            xmax = pt2[0] if pt2[0] < img.shape[1] else  img.shape[1]
            ymax = pt2[1] if pt2[1] < img.shape[0] else  img.shape[0]
            
            img=img[ymin:ymax ,xmin:xmax]
            obj_img.append(img)
            print("cut x: {} : {} y: {} : {} name : {}".format(xmin,xmax,ymin,ymax, detection[0].decode()))
        return obj_img

    def cvDrawBoxes(self,detections,img):
        for detection in detections:
            x, y, w, h = detection[2][0],\
                detection[2][1],\
                detection[2][2],\
                detection[2][3]
            xmin, ymin, xmax, ymax = self.convertBack(
                float(x), float(y), float(w), float(h),[img.shape[1],img.shape[0]],[self.resize_img.shape[1],self.resize_img.shape[0]])
            pt1 = (xmin, ymin)
            pt2 = (xmax, ymax)

            cv2.rectangle(img, pt1, pt2, (0, 255, 0), 1)
            cv2.putText(img,
                        detection[0].decode() +
                        " [" + str(round(detection[1] * 100, 2)) + "]",
                        (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        [0, 255, 0], 2)
        return img
    
    def yolo(self,img,thre = 0.8): # 回傳畫好的圖片(單張)以及切個出來的圖片(list)
        frame_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.resize_img = cv2.resize(frame_rgb,
                                   (darknet.network_width(self.netMain),
                                    darknet.network_height(self.netMain)),
                                    interpolation=cv2.INTER_LINEAR)
    
        darknet.copy_image_from_bytes(self.darknet_image,self.resize_img.tobytes())
        detections = darknet.detect_image(self.netMain, self.metaMain, self.darknet_image, thresh=thre)
        
#        image = self.cvDrawBoxes(detections, frame_resized,img)
#        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#        images = self.cut_image(detections, frame_resized,img)
        return detections



##---使用範例，記得import此檔以及相對應知dll是否有放好
#
#plateDetecter = YOLO(configPath="./cfg/yolov3-tiny-face.cfg",
#                     weightPath="./weights/yolov3-tiny-face_55000.weights",
#                     metaPath="./cfg/obj.data")#初始化yolo，給定相對應的cfg以及weight位置
#
#capture = cv2.VideoCapture("test.mp4")
#ret , frame = capture.read()
#
#while ret:
#    ret , frame = capture.read()
#    img , imgs = plateDetecter.yolo(frame) #取得計算結果 
#    cv2.imshow("test",img)
#    cv2.waitKey(10) 
#capture.release()
#cv2.destroyAllWindows()
    