'''
Created on 2 gru 2014

@author: jeedeye
'''
'''
Created on 22 paź 2014

@author: jeedeye
'''

#!/usr/bin/python3

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from bp.NeuralNetwork import NeuralNetwork
from bp.XMLParser import XMLParser
import time
import numpy as np
from itertools import cycle
from math import sqrt
import math

# consts
MAX_WINDOW = 800
NET = 6
HEIGHT = 50
WIDTH = 50
ENTRANCES = HEIGHT * WIDTH

class Image(QLabel):
    def __init__(self, parent=None):
        super(Image, self).__init__(parent)   
        self.setBackgroundRole(QPalette.Base)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setScaledContents(True)
        
    def setImage(self, image):
        self.image = image.copy()
        self.setPixmap(QPixmap.fromImage(image))
        self.repaint()
        
    def loadFromFile(self, fileName):   
        self.image = QImage(fileName)
        if self.image.isNull():
            QMessageBox.information(self, "Image Viewer",
                    "Cannot load %s." % fileName)
            return
        
        rect = self.image.rect() 
        self.image = self.image.scaled(rect.width()/2, rect.height()/2)
        self.setGeometry(self.image.rect())
        self.setPixmap(QPixmap.fromImage(self.image))
        self.scaleFactor = 1.0
        
        color = QColor(self.image.pixel(2, 4))
        print(color.red(), color.green(), color.red())
        
    def fill(self, color):
        self.image.fill(color)
        self.setPixmap(QPixmap.fromImage(self.image))
        self.repaint()
        
    def getSize(self):
        return self.image.rect()
    
    def getImage(self):
        return self.image.copy()
    
    @pyqtSlot(QImage)
    def imageChanged(self, newImage):
        self.setImage(newImage)
        #print("new image set")

        
    
class MainWidget(QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent) 
        self.parser = XMLParser()
        self.netConfig1 = [6, 4, 4, 3]
        self.netConfig2 = [6, 5, 10, 3]
        self.netConfig3 = [6, 30, 32, 10, 3]
        self.setupUI()
        
        
    def setupUI(self):                
        self.setMinimumSize(MAX_WINDOW *2 , MAX_WINDOW + 20)
        self.img = Image(self)
        self.img.loadFromFile("yoda.jpg")
        self.img.move(MAX_WINDOW - 200, 100)
        self.img.show()
        
        self.netImg1 = Image(self)
        self.netImg1.setGeometry(self.img.getSize())
        self.netImg1.setImage(self.img.image.copy())
        self.netImg1.fill(Qt.gray)
        self.netImg1.move(100, self.img.geometry().bottomRight().y() + 50)
        self.netImg1.show()
        netConfigLabel1 = QLabel(self)
        netConfigLabel1.setText(' x '.join(map(str, self.netConfig1)))
        netConfigLabel1.setGeometry(self.netImg1.geometry().bottomLeft().x() + 100, self.netImg1.geometry().bottomRight().y() + 40, 200, 50)
        netCounterLabel1 = QLabel(self)
        netCounterLabel1.setGeometry(self.netImg1.geometry().topLeft().x() + 100, self.netImg1.geometry().topRight().y() - 40, 200, 50)
        
        self.netImg2 = Image(self)
        self.netImg2.setGeometry(self.img.getSize())
        self.netImg2.setImage(self.img.image.copy())
        self.netImg2.fill(Qt.gray)
        self.netImg2.move(self.netImg1.geometry().topRight().x() + 50,  self.netImg1.geometry().topRight().y())
        self.netImg2.show()
        netConfigLabel2 = QLabel(self)
        netConfigLabel2.setText(' x '.join(map(str, self.netConfig2)))
        netConfigLabel2.setGeometry(self.netImg2.geometry().bottomLeft().x() + 100, self.netImg2.geometry().bottomRight().y() + 40, 200, 50)
        netCounterLabel2 = QLabel(self)
        netCounterLabel2.setGeometry(self.netImg2.geometry().topLeft().x() + 100, self.netImg2.geometry().topRight().y() - 40, 200, 50)
        
        self.netImg3 = Image(self)
        self.netImg3.setGeometry(self.img.getSize())
        self.netImg3.setImage(self.img.image.copy())
        self.netImg3.fill(Qt.gray)
        self.netImg3.move(self.netImg2.geometry().topRight().x() + 50, self.netImg2.geometry().topRight().y())
        self.netImg3.show()
        netConfigLabel3 = QLabel(self)
        netConfigLabel3.setText(' x '.join(map(str, self.netConfig3)))
        netConfigLabel3.setGeometry(self.netImg3.geometry().bottomLeft().x() + 100, self.netImg3.geometry().bottomRight().y() + 40, 200, 50)
        netCounterLabel3 = QLabel(self)
        netCounterLabel3.setGeometry(self.netImg3.geometry().topLeft().x() + 100, self.netImg3.geometry().topRight().y() - 40, 200, 50)
        
        self.net1 = NeuralNetwork(0, self.netConfig1, self.img.getImage())
        self.net1.imgGenerated.connect(self.netImg1.imageChanged, Qt.QueuedConnection)
        self.net1.sendWeights.connect(self.parser.setNet, Qt.QueuedConnection)
        self.net1.sendCounter.connect(netCounterLabel1.setText)
        self.net1.sendImgCounter.connect(self.parser.setImgCounter, Qt.QueuedConnection)
        self.net1.imgCounter = self.parser.getImgCounter(self.net1.id)
        self.net1.setWeights(self.parser.getNet(self.net1.id))
        
        self.net2 = NeuralNetwork(1, self.netConfig2, self.img.getImage())
        self.net2.imgGenerated.connect(self.netImg2.imageChanged, Qt.QueuedConnection)
        self.net2.sendWeights.connect(self.parser.setNet, Qt.QueuedConnection)
        self.net2.sendCounter.connect(netCounterLabel2.setText)
        self.net2.sendImgCounter.connect(self.parser.setImgCounter, Qt.QueuedConnection)
        self.net2.imgCounter = self.parser.getImgCounter(self.net2.id)
        self.net2.setWeights(self.parser.getNet(self.net2.id))
        
        self.net3 = NeuralNetwork(2, self.netConfig3, self.img.getImage())
        self.net3.imgGenerated.connect(self.netImg3.imageChanged, Qt.QueuedConnection)
        self.net3.sendWeights.connect(self.parser.setNet, Qt.QueuedConnection)
        self.net3.sendCounter.connect(netCounterLabel3.setText)
        self.net3.sendImgCounter.connect(self.parser.setImgCounter, Qt.QueuedConnection)
        self.net3.imgCounter = self.parser.getImgCounter(self.net3.id)
        self.net3.setWeights(self.parser.getNet(self.net3.id))
        
        self.net1.start()
        self.net2.start()
        self.net3.start()
        
        
        
    def __del__(self):
        self.net1.terminate()
        self.net2.terminate()
        self.net3.terminate()
        
        


class Form(QMainWindow):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("PerceptronPicture")
        self.mainWidget = MainWidget()
    
        #self.mainWidget.setStyleSheet("QWidget { background-color: blue; }")
        self.statusBar = QStatusBar()
    
        self.setCentralWidget(self.mainWidget)
        self.setStatusBar(self.statusBar)

    
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    screen = Form()
    screen.show()
    sys.exit(app.exec_())