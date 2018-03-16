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
from XMLParser import XMLParser
from Graph import Graph, NodePoint
import math

# consts
MAX_WINDOW = 800
NET = 6
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
        self.randomPoints = []
        self.chosenPoint = QPointF()
        self.graph = Graph()
        self.graph.prepareNet(NET, MAX_WINDOW)
        self.cloudPointMode = True
        self.netCounter = 0
        self.setFocus()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        brush = QBrush(Qt.black)
        pen = QPen(Qt.black)
        painter.setPen(pen)
        painter.fillRect(event.rect(), brush)
        #draw pixels
        if self.cloudPointMode:
            for row in self.pixels:
                for pixel in row:
                    if pixel.on == -1:
                        brush = QBrush(Qt.black)
                    elif pixel.on == 1:
                        brush = QBrush(Qt.red)
                    painter.fillRect(pixel, brush)
        else:
            # draw points
            brush = QBrush(Qt.blue)
            pen = QPen(Qt.blue)
            painter.setPen(pen)
            for point in self.randomPoints:
                painter.drawLine(QLine(QPoint(point.x() - 3.0, point.y()-3.0), QPoint(point.x() + 3.0, point.y() + 3.0)))
                painter.drawLine(QLine(QPoint(point.x() - 3.0, point.y()+3.0), QPoint(point.x() + 3.0, point.y() - 3.0)))
            # draw chosen point:
            
            pen = QPen(Qt.yellow)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawEllipse(QPointF(self.chosenPoint.x(), self.chosenPoint.y()), 6, 6)
            brush = QBrush(Qt.green)
            pen = QPen(Qt.black)
            pen.setWidth(4)
            painter.setPen(pen)
            painter.drawLine(QLine(QPoint(self.chosenPoint.x() - 4.0, self.chosenPoint.y()-4.0), QPoint(self.chosenPoint.x() + 4.0, self.chosenPoint.y() + 4.0)))
            painter.drawLine(QLine(QPoint(self.chosenPoint.x() - 4.0, self.chosenPoint.y()+4.0), QPoint(self.chosenPoint.x() + 4.0, self.chosenPoint.y() - 4.0)))

            #draw edges
            pen = QPen(Qt.white)
            pen.setWidth(2)
            painter.setPen(pen)
            edges = []
            for node in self.graph.get_vertices():
                for neighbour in self.graph.get_vertex(node).get_connections():
                    edges.append((self.graph.get_vertex(node).nodePoint, neighbour.nodePoint))
            for edge in edges:
                painter.drawLine(QLineF(edge[0].x(), edge[0].y(), edge[1].x(), edge[1].y()))
            #draw nodes
            brush = QBrush(Qt.red)
            pen = QPen(Qt.red)
            pen.setWidth(3)
            painter.setPen(pen)
            for node in self.graph.get_vertices():
                painter.drawEllipse(QPointF(self.graph.get_vertex(node).nodePoint.x(), self.graph.get_vertex(node).nodePoint.y()), 3, 3)
                #painter.drawText(QPointF(self.graph.get_vertex(node).nodePoint.x(), self.graph.get_vertex(node).nodePoint.y()), node)
            
        
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
        self.graph = Graph()
        self.graph.prepareNet(NET, MAX_WINDOW)
        self.cloudPointMode = True
        self.repaint()
    
    def getRandomPoints(self, count):
        randomPoints = []
        for x in range(1000 * count):
            randomPoint = QPoint(np.random.randint(0,MAX_WINDOW), np.random.randint(0,MAX_WINDOW))
            for row in self.pixels:
                for pixel in row:
                    if pixel.on == 1.0:
                        if pixel.contains(randomPoint):
                            randomPoints.append(randomPoint)
                            if len(randomPoints) >= count :
                                self.randomPoints = randomPoints
                                self.cloudPointMode = False
                                self.netCounter = 0
                                self.timer = QTimer()
                                self.timer.timeout.connect(self.netLearn)
                                self.timer.start(10)
                                #self.netLearn(100)
                                
                                return
                            #print(randomPoint)
                            break;
            
    
        
    def netLearn(self):
        count = 1000
        t = self.netCounter
        def d(x1, y1, x2, y2):
            return math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 )
        def G(lam, v, m):
            edgeDiff = len(self.graph.getShortest(v, m)) - 1
            #if edgeDiff <= lam:
            result = math.exp(-((edgeDiff ** 2)/(2*(lam**2))))
           # else:
            #    result = 0
            #print( "edge diff: %s result %s" % (str(edgeDiff), str(result)))
            return result
        def a(t):
            result = 1.0 - ((t-1.0)/count)
            #print ("a(t) =  " + str(result))
            return result
        
        minDistNode = '0'
        minDist = MAX_WINDOW + 100
        randPoint = self.randomPoints[np.random.randint(0, len(self.randomPoints))]
        self.chosenPoint.setX(randPoint.x()),
        self.chosenPoint.setY(randPoint.y())
        for node in self.graph.get_vertices():
            dist = d(self.graph.get_vertex(node).nodePoint.x(), self.graph.get_vertex(node).nodePoint.y(), randPoint.x(), randPoint.y())
            if dist < minDist:
                minDist = dist
                minDistNode = node
        #print("Min distance: %s for node: %s" % (str(minDist),minDistNode))
        for node in self.graph.get_vertices():
            x = self.graph.get_vertex(node).nodePoint.x() + a(t) * G(2, minDistNode, node) * (randPoint.x() - self.graph.get_vertex(node).nodePoint.x())
            y = self.graph.get_vertex(node).nodePoint.y() + a(t) * G(2, minDistNode, node) * (randPoint.y() - self.graph.get_vertex(node).nodePoint.y())
            self.graph.updateNode(node, x, y)
        self.repaint()
        self.netCounter += 1
        
        if self.netCounter >= count:
            self.timer.stop()
                
            
            
        
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
        self.setupUI()
        
        
    def setupUI(self):                
        self.setMinimumSize(MAX_WINDOW + 100, MAX_WINDOW + 20)
        
        # user pixel matrix
        self.wid1 = UserPaint(self)
        self.wid1.setGeometry(10, 10, MAX_WINDOW, MAX_WINDOW)
        self.wid1.show()
        self.wid1.setAutoFillBackground(True)
        
        # net pixel matrix
        

        self.check = QPushButton("CHECK", self)
        self.check.setGeometry(MAX_WINDOW + 20, 270, 60, 30)
        self.check.clicked.connect(self.test)
        
        self.check = QPushButton("NEXT", self)
        self.check.setGeometry(MAX_WINDOW + 20, 330, 60, 30)
        self.check.clicked.connect(self.learn)
        
        self.clearExample = QPushButton("CLEAR", self)
        self.clearExample.setGeometry(MAX_WINDOW + 20, 500, 60, 30)
        self.clearExample.clicked.connect(self.clear)
                
        # show test result
        #testLabel = QLabel("<b><FONT SIZE = 4>Rezultat klasyfikacji: </b>", self)
        #testLabel.setGeometry(MAX_WINDOW + 50, 100,250 , 30)
        
    def learn(self):
        
        self.wid1.netLearn(1000)

            
    def test(self):
        anyPixels = False
        for row in self.wid1.pixels:
            for pixel in row:
                if pixel.on > 0.0:
                    anyPixels = True
        if anyPixels:
            self.wid1.getRandomPoints(100)
            self.wid1.repaint()

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