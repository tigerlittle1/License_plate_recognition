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
import MainWindow
from PyQt5.QtGui import QImage, QPixmap


class mainWindows(QMainWindow):
    def __init__(self):
        # --------------------------設定視窗----------------------------------------------
        super().__init__()
        self.ui = MainWindow.Ui_MainWindow()
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
                     weightPath="./weights/yolov3-tiny_plate_newAnchors_25000.weights",
                     metaPath="./cfg/plate/obj.data")
        
        #--------------------------文字辨識-----------------------------------------------
        self.charDetecter = YOLO(configPath="./cfg/char/yolov3-tiny_plate_char.cfg",
                     weightPath="./weights/yolov3-tiny_plate_char_last.weights",
                     metaPath="./cfg/char/obj.data")#初始化yolo，給定相對應的cfg以及weight位置
        #-------------------------其他變數------------------------------------------------
        
        self.capture = cv2.VideoCapture("422267.t.mp4")
        self.plate_number = 0 #車牌數量
        self.plate_cap = 20   #車牌數量上限
        
    def startAndStopButton(self):
        if not self.timer.isActive():
            self.timer.start(5)
            self.ui.startButton.setText("暫停偵測")
        else:
            self.timer.stop()
            self.ui.startButton.setText("開始偵測")
            
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
        
    def cvImgConvertToQImage(self, sourceImg, BGR2RGB=False):
        rgbImage = cv2.cvtColor(sourceImg, cv2.COLOR_BGR2RGB) if BGR2RGB else sourceImg
        height, width, channel = rgbImage.shape
        rgbImage = QImage(rgbImage.data ,width ,height ,channel * width ,QImage.Format_RGB888)

        return rgbImage

                
    def detectPlate(self):
        
        ret , frame = self.capture.read()
        detecter = self.plateDetecter.yolo(self.Preprocessing.lightProcessing(frame)) #取得計算結果 
        img = self.plateDetecter.cvDrawBoxes(detecter,frame)
        img = cv2.resize(img,(541,341),interpolation=cv2.INTER_LINEAR)
        imgs = self.plateDetecter.cut_image(detecter,frame)
        self.ui.label.setPixmap(QPixmap.fromImage(self.cvImgConvertToQImage(img)))
        return imgs

    def detectChar(self,plates):
        
        for plate in plates:
            detecter = self.charDetecter.yolo(plate,0.7)
            img = self.charDetecter.cvDrawBoxes(detecter,plate)
            chart_x = []
            for d in detecter:
                chart_x.append((d[2][0],d[0].decode()))
            chart_x.sort()
            result = ""
            for c in chart_x:
                result+=c[1]
            self.addtable(self.cvImgConvertToQImage(cv2.resize(img,(160,90),interpolation=cv2.INTER_LINEAR)),result)
            
    def main_func(self):
        plates = self.detectPlate()
        self.detectChar(plates)
   
def main():
    app = QApplication(sys.argv)
    windows = mainWindows()
    windows.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()