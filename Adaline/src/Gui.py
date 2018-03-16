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
from math import sqrt
from Adaline import Adaline, AdalinePool
from XMLParser import XMLParser

# consts
MAX_WINDOW = 600
PERCEPTRONS = 10
HEIGHT = 7
WIDTH = 6
ENTRANCES = HEIGHT * WIDTH

class ErrorField(QWidget):
    def __init__(self, parent = None):
        super(ErrorField, self).__init__(parent)
        self.setStyleSheet("QWidget { background-color: white; }")
        
        self.setAutoFillBackground(True)
        self.points = []
        self.color = Qt.red
        self.currentNumber = 0
        self.numberLabel = QLabel("Error chart for digit #", self)
        self.maxError = 1.0
        self.show()
        
    def paintEvent(self, event):
        self.numberLabel.setGeometry(self.geometry().width()//2 - 100, 10 ,200, 30 )
        painter = QPainter(self)
        brush = QBrush(Qt.black)
        pen = QPen(Qt.white)
        pen.setWidth(1)
        painter.fillRect(event.rect(), brush)
        # painter.setRenderHint(QPainter.Antialiasing, self.antialiased)
        brush.setColor(Qt.white)
        pen.setColor(self.color)
        self.height = self.geometry().height()
        self.width = self.geometry().width()
        for ver in range(0, self.width, self.width // 10):
            painter.drawLine(QPoint(ver, 0), QPoint(ver, self.height))
            
        counter = 0
        for hor in range(0, self.height, self.height // 4):
            label = QLabel("{0:.4f}".format(self.maxError - (self.maxError/4) * counter), self)
            label.setGeometry(10, hor + 5, 100, 30)
            label.show()
            painter.drawLine(QPoint(0, hor), QPoint(self.width, hor))
            counter += 1
            
        brush.setColor(Qt.white)
        pen.setColor(self.color)
        painter.setPen(pen)
        for i in range(len(self.points) - 1 ):
            painter.drawLine(self.points[i], self.points[i+1])
            
    def setErrorPoints(self, adaline):
        points = []
        errorPoints = adaline.errors
        number = adaline.myDigit
        #maxPoint = max(errorPoints)
        maxPoint = 10
        self.maxError = maxPoint
        height = self.geometry().height()
        for i in range(len(errorPoints)):
            points.append(QPoint(i + self.width//10 + 10, height - (errorPoints[i] * height)//maxPoint))
        self.points = points
        self.numberLabel.setText("Error chart for digit " + str(number))
        self.repaint()
        
            
class Field(QWidget):
    
    changed = pyqtSignal(int, float)
    
    def __init__(self, position):
        super(Field, self).__init__()
        self.on = False
        self.position = position
        self.positionLabel = QLabel(str(self.position), self)
        self.positionLabel.setGeometry(self.geometry())
        self.positionLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.positionLabel.setAlignment(Qt.AlignCenter)
        self.positionLabel.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QWidget { background-color: grey; }")
        self.show()
        self.setAutoFillBackground(True)
        
    def mousePressEvent(self, QMouseEvent):
        #print( str(QMouseEvent.pos()) + " Position:" + str(self.position))
        if self.on == 1.0:
            self.on = -1.0
            self.setStyleSheet("QWidget { background-color: grey; }")
            self.show()
            self.setAutoFillBackground(True)
            self.changed.emit(self.position, self.on)
        else:
            self.on = 1.0
            self.setStyleSheet("QWidget { background-color: red; }")
            self.show()
            self.setAutoFillBackground(True)
            self.changed.emit(self.position, self.on)
    
    
class MainWidget(QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        
        self.isCurrExProper = False
        self.pixelMap = np.array([-1.0 for i in range(ENTRANCES)])
        self.currentAdalineIndex = 0
        
        self.xmlParser = XMLParser()
        self.examples = self.xmlParser.getAllExamples()
        
        self.adalines = [Adaline(myDigit = i, examples = self.examples, weightsCount = ENTRANCES) for i in range(PERCEPTRONS)]
        #for perc in self.adalines:
        #    perc.setWeights(self.xmlParser.getWeights(perc.getMyDigit()))
        
        self.setupUI()
        
        
    def setupUI(self):                
        self.setMinimumSize(MAX_WINDOW * 3, MAX_WINDOW + 400)
        
        # pixel matrix
        wid1 = QWidget(self)
        wid1.setGeometry(10, 10, MAX_WINDOW, MAX_WINDOW)
        wid1.setStyleSheet("QWidget {background-color: black }")
        wid1.show()
        wid1.setAutoFillBackground(True)
        
        pixels = [Field(i) for i in range(ENTRANCES)]
        for pixel in pixels:
            pixel.changed.connect(self.pixelChanged)
        pixelsLay = QGridLayout()
        for i in range(HEIGHT):
            for j in range(WIDTH):
                pixelsLay.addWidget(pixels[i * WIDTH + j], i, j)
        wid1.setLayout(pixelsLay)
        
        # add example
        
        addExLabel = QLabel("<b><FONT SIZE = 4>Dodaj przyklad dla cyfry: </b>", self)
        addExLabel.setGeometry(MAX_WINDOW + 50, 10, 250, 30)
        
        self.addExText = QTextEdit(self)
        self.addExText.setGeometry(MAX_WINDOW + 300, 10, 50, 30)
        
        self.isProperButton = QPushButton("NIEPOPRAWNY", self)
        self.isProperButton.setGeometry(MAX_WINDOW + 370, 10, 120, 30)
        self.isProperButton.clicked.connect(self.changeCurrExProper)
        
        self.addExButton = QPushButton("DODAJ", self)
        self.addExButton.setGeometry(MAX_WINDOW + 500, 10, 70, 30)
        self.addExButton.clicked.connect(self.addExample)
        
        # show test result
        testLabel = QLabel("<b><FONT SIZE = 4>Rezultat klasyfikacji: </b>", self)
        testLabel.setGeometry(MAX_WINDOW + 50, 100,250 , 30)
        
        self.resultLabel = QLabel("<b><h1>3</h1></b>", self)
        self.resultLabel.setGeometry(MAX_WINDOW + 50, 150, 400 , 100)
        # learn  
        self.learnLabel = QLabel("<b><FONT SIZE = 4>Status uczenia: nie rozpoczeto</b>", self)
        self.learnLabel.setGeometry(MAX_WINDOW + 50, MAX_WINDOW - 50, 400 , 30)
        
        self.learnButton = QPushButton("UCZ", self)
        self.learnButton.setGeometry(MAX_WINDOW + 400, MAX_WINDOW - 50, 100, 30)
        self.learnButton.clicked.connect(self.learnAdalines)
        
        self.errorWid = ErrorField(self)
        self.errorWid.setGeometry(10, MAX_WINDOW, MAX_WINDOW * 3, 400)
        
        self.nextChartButton = QPushButton("CHART >>", self)
        self.nextChartButton.setGeometry(MAX_WINDOW + 500, MAX_WINDOW - 200, 70, 30)
        self.nextChartButton.clicked.connect(self.nextChart)
        
        
    def nextChart(self):
        self.currentAdalineIndex = (self.currentAdalineIndex + 1) % len(self.adalines)
        self.errorWid.setErrorPoints(self.adalines[self.currentAdalineIndex])
        
    def changeCurrExProper(self):
        if self.isCurrExProper:
            self.isCurrExProper = False
            self.isProperButton.setText("NIEPOPRAWNY")
        else:
            self.isCurrExProper = True
            self.isProperButton.setText("POPRAWNY")
            
    def testPixels(self):
        result = [perc.isThatYourNumber(self.pixelMap) for perc in self.adalines]
        print(result)
        result = list(filter(lambda x: x >= 0, result))
        
        result = map(str, result)
        if result:
            testText = '<b>' + ' or '.join(result) + '</b>'
        else:
            testText = '<b>no classification</b>'
        self.resultLabel.setText(testText)
        self.resultLabel.setStyleSheet("font: %spt;" % str(48/(1+len(list(result)))));
        self.resultLabel.show()
        
    @pyqtSlot(int, float)
    def pixelChanged(self, pos, val):
        self.pixelMap[pos] = val
        self.testPixels()
        #print ("Pixel: %s value: %s" % (str(pos), str(val)))
        #print (self.pixelMap)
       
    def addExample(self): 
        number = int(self.addExText.toPlainText())
        self.xmlParser.addExample(number, self.pixelMap, self.isCurrExProper)
        
    def learnAdalines(self):
        self.learnLabel.setText("<b><FONT SIZE = 4>Status uczenia: w toku...</b>")
        self.learnLabel.show()
        percPool = AdalinePool(self.adalines, self.examples)
        beforeTime = time.process_time()
        self.adalines = percPool.learnPerc()
        learnTime = elapsed_time = time.process_time() - beforeTime
        for perc in self.adalines:
            self.xmlParser.setWeights(perc.getMyDigit(), perc.getWeights()) 
        self.xmlParser.saveXml()
        #self.adalines[0].start()
        #self.adalines[0].join()
        self.learnLabel.setText("<b><FONT SIZE = 4>Status uczenia: zakonczono (%s)</b>" % str(learnTime))

class Form(QMainWindow):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)
        self.setWindowTitle("Adaline")
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