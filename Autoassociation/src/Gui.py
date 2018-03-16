'''
Created on 22 paź 2014

@author: jeedeye
'''

#!/usr/bin/python3

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import time
import numpy as np
from itertools import cycle
from math import sqrt
from Perceptron import Perceptron, PerceptronPool
from XMLParser import XMLParser

# consts
MAX_WINDOW = 600
PERCEPTRONS = 10
HEIGHT = 50
WIDTH = 50
ENTRANCES = HEIGHT * WIDTH

class Pixel(QRect):
    def __init__(self, x, y):
        self.posX = x 
        self.posY = y
        self.boundary = MAX_WINDOW//WIDTH
        super(Pixel, self).__init__(self.posX * self.boundary, self.posY * self.boundary, self.boundary, self.boundary)
        self.on = -1
        

class Field(QWidget):
    
    def __init__(self, parent=None):
        super(Field, self).__init__(parent)
        self.pixels = []
        for row in range(WIDTH):
            self.pixels.append([Pixel( row, column) for column in range(HEIGHT)])
        #for pixel in self.pixels:
        #    print("x: %s, y: %s, width: %s, height: %s" % (pixel.x(), pixel.y(), pixel.width(), pixel.height()))
        self.setFocus()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        brush = QBrush(Qt.black)
        pen = QPen(Qt.black)
        painter.setPen(pen)
        painter.fillRect(event.rect(), brush)
        for row in self.pixels:
            for pixel in row:
                if pixel.on == -1:
                    brush = QBrush(Qt.black)
                elif pixel.on == 1:
                    brush = QBrush(Qt.red)
                painter.fillRect(pixel, brush)
        
    def getPixelMap(self):
        pixelMap = []
        for row in self.pixels:
            pixelMap.append(np.array( [pixel.on for pixel in row] ))
        return pixelMap
    
    def setPixelMap(self, pixelMap):
        for i in range(len(pixelMap)):
            for j in range(len(pixelMap[0])):
                self.pixels[i][j].on = pixelMap[i][j]
        self.repaint()
        
    def clear(self):
        for i in range(len(self.pixels)):
            for j in range(len(self.pixels[0])):
                self.pixels[i][j].on = -1
        self.repaint()
        
        
            
class NetPaint(Field):
    def __init__(self, parent=None):
        super(NetPaint, self).__init__(parent)
        
class UserPaint(Field):
    #changed = pyqtSignal(int, float)
    
    def __init__(self, parent=None):
        super(UserPaint, self).__init__(parent)
        self.paintingModeOn = False
        self.eraseModeOn = False
        
    def mousePressEvent(self, QMouseEvent):
        self.setFocus()
        mousePos = QMouseEvent.pos()
        if QMouseEvent.button() == Qt.LeftButton:
            self.paintCircle(mousePos, color = 1)
            self.paintingModeOn = True
        if QMouseEvent.button() == Qt.RightButton:
            self.paintCircle(mousePos, color = -1)
            self.eraseModeOn = True
    
    def mouseMoveEvent(self, QMouseEvent):
        mousePos = QMouseEvent.pos()
        if self.paintingModeOn:
            self.paintCircle(mousePos, color = 1)
        if self.eraseModeOn:
            self.paintCircle(mousePos, color = -1)
    
    def mouseReleaseEvent(self, QMouseEvent):
        self.paintingModeOn = False
        self.eraseModeOn = False
            
            
    def paintCircle(self, mousePos, color):
        for i in range(len(self.pixels)):
            for j in range (len(self.pixels[0])):
                if self.pixels[i][j].contains(mousePos):
                    for y in range(-2, 2):
                        for x in range(-2, 2):
                            if i+x >= 0 and j+y >= 0 and i+x <= WIDTH-1 and j+y <= HEIGHT-1:
                                self.pixels[i+x][j+y].on = color
                    #print("found pixel")
                    break
        self.repaint()
        
    
    
class MainWidget(QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        
        self.xmlParser = XMLParser()
        self.examples = self.xmlParser.getAllExamples()
        self.currentExampleIndex = 0
        self.currentExample = self.examples[self.currentExampleIndex]
        self.percInfo = self.xmlParser.getAllPerceptrons()
        self.perceptrons = []
        for i in range(HEIGHT):
            row = []
            for j in range(WIDTH):
                perc = Perceptron(i,j, self.examples, ENTRANCES)
                perc.setWeights(newWeights = self.percInfo[i][j][1], newTheta = self.percInfo[i][j][0])
                row.append(perc)
            self.perceptrons.append(row)
        
        self.setupUI()
        
        
    def setupUI(self):                
        self.setMinimumSize(MAX_WINDOW * 2 + 200, MAX_WINDOW + 20)
        
        # user pixel matrix
        self.wid1 = UserPaint(self)
        self.wid1.setGeometry(10, 10, MAX_WINDOW, MAX_WINDOW)
        self.wid1.show()
        self.wid1.setAutoFillBackground(True)
        
        # net pixel matrix
        
        self.wid2 = NetPaint(self)
        self.wid2.setGeometry(MAX_WINDOW + 100, 10, MAX_WINDOW, MAX_WINDOW)
        self.wid2.show()
        self.wid2.setAutoFillBackground(True)
        # add example
        
        self.nextExample = QPushButton(">>", self)
        self.nextExample.setGeometry(MAX_WINDOW + 20, 210, 60, 30)
        self.nextExample.clicked.connect(self.next)
        
        self.prevExample = QPushButton("<<", self)
        self.prevExample.setGeometry(MAX_WINDOW + 20, 240, 60, 30)
        self.prevExample.clicked.connect(self.prev)

        self.check = QPushButton("CHECK", self)
        self.check.setGeometry(MAX_WINDOW + 20, 270, 60, 30)
        self.check.clicked.connect(self.test)

        self.recurse = QPushButton("RECUR", self)
        self.recurse.setGeometry(MAX_WINDOW + 20, 300, 60, 30)
        self.recurse.clicked.connect(self.recursive)
        
        self.saveExample = QPushButton("SAVE", self)
        self.saveExample.setGeometry(MAX_WINDOW + 20, 330, 60, 30)
        self.saveExample.clicked.connect(self.save)
        
        self.clearExample = QPushButton("CLEAR", self)
        self.clearExample.setGeometry(MAX_WINDOW + 20, 500, 60, 30)
        self.clearExample.clicked.connect(self.clear)
                
        # show test result
        #testLabel = QLabel("<b><FONT SIZE = 4>Rezultat klasyfikacji: </b>", self)
        #testLabel.setGeometry(MAX_WINDOW + 50, 100,250 , 30)
        

    def next(self):
        self.currentExampleIndex = (self.currentExampleIndex + 1) % len(self.examples)
        self.currentExample = self.examples[self.currentExampleIndex]
        self.wid1.setPixelMap(self.currentExample)
        
    def prev(self):
        self.currentExampleIndex = (self.currentExampleIndex + 1) % len(self.examples)
        self.currentExample = self.examples[self.currentExampleIndex]
        self.wid1.setPixelMap(self.currentExample)
            
    def test(self):
        pixelMap = self.wid1.getPixelMap()
        resultMap = []
        for i in range(len(self.perceptrons)):
            row = []
            for j in range(len(self.perceptrons[0])):
                row.append(self.perceptrons[i][j].classify(pixelMap))
            resultMap.append(np.array(row))
        self.wid2.setPixelMap(resultMap)
       
    def save(self): 
        self.xmlParser.addExample( self.wid1.getPixelMap())
        
    def recursive(self):
        self.wid1.setPixelMap(self.wid2.getPixelMap())
        self.test()
        
    def clear(self):
        self.wid1.clear()
        


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