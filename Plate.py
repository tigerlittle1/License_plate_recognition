# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 00:05:42 2019

@author: harry
"""
import sys
from YOLO_Class import YOLO
from plate_Preprocessing import Preprocessing 
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QHBoxLayout, QWidget, QTableWidgetItem
from PyQt5.QtCore import QTimer, Qt
import MainWindow3
from PyQt5.QtGui import QImage, QPixmap
import threading
import time
import queue  

class mainWindows(QMainWindow):
    def __init__(self):
        # --------------------------設定視窗----------------------------------------------
        super().__init__()
        self.ui = MainWindow3.Ui_MainWindow()
        self.ui.setupUi(self)

        self.timer = QTimer()
        self.timer.timeout.connect(self.main_func)
        self.ui.startButton.clicked.connect(self.startAndStopButton)
        self.ui.tableWidget.setColumnCount(2)
        self.ui.tableWidget.setHorizontalHeaderLabels(["車牌","結果"])
        self.ui.tableWidget.setColumnWidth(0, 200)
        #--------------------------影像預處理---------------------------------------------
        self.Preprocessing = Preprocessing()
        #--------------------------車牌偵測-----------------------------------------------
        self.plateDetecter = YOLO(configPath="./cfg/plate/yolov3-tiny_plate_newAnchors.cfg",
                     weightPath="./weights/yolov3-tiny_plate_newAnchors_last.weights",
                     metaPath="./cfg/plate/obj.data")
        
        #--------------------------文字辨識-----------------------------------------------
        self.charDetecter = YOLO(configPath="./cfg/char/yolov3-tiny_plate_char.cfg",
                     weightPath="./weights/yolov3-tiny_plate_char_last0112.weights",
                     metaPath="./cfg/char/obj.data")#初始化yolo，給定相對應的cfg以及weight位置
        #-------------------------其他變數------------------------------------------------
        
        self.capture = cv2.VideoCapture(r"D:\License_plate_recognition\test_video\Y4.mov")
        print(self.capture)
        self.plate_number = 0 #車牌數量
        self.plate_cap = 20   #車牌數量上限
        self.ret = True
        self.Pending_image = queue.Queue(0)
        self.Current_image = None
        self.sart_time = 0
        self.end_time = 0
        self.capture.set(0,60*1000);
        
        
        
#        self.cam_thread = threading.Thread(target = self.get_image)
#        self.cam_thread.start()
        
    def startAndStopButton(self):
        if not self.timer.isActive():
            self.timer.start(5)
            self.ui.startButton.setText("暫停偵測")
        else:
            self.timer.stop()
            self.ui.startButton.setText("開始偵測")
            
    def closeEvent(self,event):#函数名固定不可变
        self.capture.release()
        cv2.destroyAllWindows()
        
    def addtable(self,image,text):
        
        row =  self.plate_number % self.plate_cap
        self.ui.tableWidget.setRowCount(row+1)
        self.ui.tableWidget.setRowHeight(row,90)
        label = QLabel("")
        label.setAlignment(Qt.AlignCenter)  # 水平居中
        label.setPixmap(QPixmap.fromImage(image))  # 只有圖片
        
        h = QHBoxLayout()
        h.setAlignment(Qt.AlignCenter)
        h.addWidget(label)
        w = QWidget()
        w.setLayout(h)
    
        self.ui.tableWidget.setCellWidget(row,0,w)
        self.ui.tableWidget.setItem(row,1,QTableWidgetItem(text))
        self.plate_number += 1
        print(self.plate_number)
       
    def get_image(self):
        while self.ret :
            self.ret , frame = self.capture.read()
            self.Pending_image.put(self.Preprocessing.lightProcessing(frame))
        
    def cvImgConvertToQImage(self, sourceImg, BGR2RGB=True):
        rgbImage = cv2.cvtColor(sourceImg, cv2.COLOR_BGR2RGB) if BGR2RGB else sourceImg
        height, width, channel = rgbImage.shape
        rgbImage = QImage(rgbImage.data ,width ,height ,channel * width ,QImage.Format_RGB888)

        return rgbImage

                
    def detectPlate(self):

        self.ret , frame = self.capture.read()
        self.Current_image = self.Preprocessing.lightProcessing(frame).copy()
#        self.Current_image = self.Preprocessing.unevenLightCompensate(self.Current_image)
#        lower_read = np.array([0, 0, 0]) ##[R value, G value, B value]
#        upper_read = np.array([200, 200, 255]) 
#        mask = cv2.inRange(self.Current_image, lower_read, upper_read)  
#        self.Current_image[mask == 0] = [200,200, 255]

        if not self.ret:
            return None
        
        #self.Current_image = self.Pending_image.get()
        detecter = self.plateDetecter.yolo(self.Current_image,0.75) #取得計算結果 
        img = self.plateDetecter.cvDrawBoxes(detecter,self.Current_image)
        img = cv2.resize(self.Current_image,(int(img.shape[1]*0.5),int(img.shape[0]*0.5)),interpolation=cv2.INTER_LINEAR)
        imgs = self.plateDetecter.cut_image(detecter,frame)
        self.ui.label.setPixmap(QPixmap.fromImage(self.cvImgConvertToQImage(img)))

        return imgs


    def detectChar(self,plates):
        #str(round(detection[1] * 100, 2))
        for plate in plates:
#            cv2.imshow("rotimg",plate)
#            plate = self.Preprocessing.rotImg(plate)
#            cv2.imshow("rotimging",plate)
#            cv2.waitKey(1)
            detecter = self.charDetecter.yolo(plate,0.6)
            img = self.charDetecter.cvDrawBoxes(detecter,plate)
            chart_x = []
            
#            for i in detecter:
#                add = True
#                for j in detecter:
#                    print(i[2][0]==j[2][0])
#                    if i[2][0]==j[2][0] <= 0.1 and i[0] != j[0]:
                        
                        

            for d in detecter:
                chart_x.append((d[2][0],d[0].decode()))
            chart_x.sort()
            
            result = ""
            for c in chart_x:
                result+=c[1]
            self.addtable(self.cvImgConvertToQImage(cv2.resize(img,(160,90),interpolation=cv2.INTER_LINEAR)),result)
            
            
    def main_func(self):
        self.sart_time = time.time()
        plates = self.detectPlate()
        if plates:
            self.detectChar(plates)
        self.end_time = time.time()
        print("處理時間 : {}".format(self.end_time-self.sart_time))
        
   
def main():
    app = QApplication(sys.argv)
    windows = mainWindows()
    windows.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()