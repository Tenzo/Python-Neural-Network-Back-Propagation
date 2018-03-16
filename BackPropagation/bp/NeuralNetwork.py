'''
Created on 5 gru 2014

@author: jeedeye
'''
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import numpy as np
from math import exp, sin, pi

class Layer:
    def __init__(self, inputNo, neuronsNo):
        self.eta = 0.5
        self.X = np.array([])
        self.weights = np.random.random_sample((inputNo + 1, neuronsNo))/1000
        self.A = np.array([0 for i in range(neuronsNo)])
        self.Y = np.array([0 for i in range(neuronsNo)])
        self.diff = np.array([0 for i in range(neuronsNo)])
        self.D = np.array([0 for i in range(neuronsNo)])
        
    def sig(self, x):
        try:
            expect = (1/(1 + exp(-x))) 
            return expect
        except Exception:
            return 1e-300
    
    def sigDiff(self, x):
        return x * (1 - x)
    
    def feed(self, input):
        self.X = np.append(input, [-1.0], 0)
        self.A = np.dot(self.X, self.weights)
        
        self.Y = self.__map_for(self.A, self.sig)
        self.D = self.__map_for(self.Y, self.sigDiff)
        #self.D = np.array(list(map(self.sigDiff, self.A)))#(self.output, self.sigDiff)
        #self.Y = np.array(list(map(self.sig, self.A)))
        
    def lastLayerFeedBack(self, rgb):
        #print(self.output)
        self.diff = (self.Y - np.array(rgb)) * self.D
        
    def feedBack(self, frontLayer):
        #sumsDW = np.dot(frontLayer.getDiffs(), np.transpose(frontLayer.getWeights()[:-1,:]))
        eps = np.dot(frontLayer.getDiffs(), frontLayer.getWeights()[:-1,:].T)
        self.diff = eps * self.D
        #print(fixMatrix)
    def fixWeights(self):
        #fixMatrix = (self.eta * np.array([self.diff for i in range(len(self.X))]) * np.transpose(np.array([self.X for i in range(len(self.diff))])))
        fixMatrix = self.eta * self.X * self.diff[np.newaxis].T 
        self.weights = self.weights - fixMatrix.T
        
    def __map_for(self,a, f):
        c = a.copy()
        c = c.reshape(-1)
        for i, v in enumerate(c):
            c[i] = f(v)
        return c
    
        #print(self.diff)
    
    def getA(self):
        return self.A
    
    def getY(self):
        return self.Y
    
    def getDiffs(self):
        return self.diff
        
    def getD(self):
        return self.D

    def getWeights(self):
        return self.weights
    
    def setWeights(self, newWeights):
        #print("Old weights: %s, new weights: %s" % (str(len(self.weights)), str(len(newWeights))))
        self.weights = newWeights

class NeuralNetwork(QThread):
    
    imgGenerated = pyqtSignal(QImage)
    sendWeights = pyqtSignal(int, list)
    sendCounter = pyqtSignal(str)
    sendImgCounter = pyqtSignal(int, int)
    
    def __init__(self, id, layerStructure, image):
        QThread.__init__(self)
        self.imgFileName = '/home/jeedeye/workspace/BackPropagation/img/output_net_'+ str(id) + '_' + 'x'.join(map(str, layerStructure)) + '_'
        self.id = id
        self.imgCounter = 0
        self.image = image
        self.myNetImage = image.copy()
        self.myNetImage.fill(Qt.gray)
        self.layers = []
        self.generateLayers(layerStructure)
        self.doRun = True
        #self.timer = QTimer()
        #self.timer.timeout.connect(self.getLearnedImage)
        self.counter = 0 
    def __del__(self):
        self.doRun = False
        self.wait()
        
    def generateLayers(self, layerStructure):
        for i in range(len(layerStructure)-1):
            self.layers.append(Layer(layerStructure[i], layerStructure[i + 1]))
        #print(self.layers)
        
    def generatePicture2(self):
        print("Generating picture")
        for x in range(self.myNetImage.width()):
            for y in range(self.myNetImage.height()):
                x1 = x/self.myNetImage.width()
                y1 = y/self.myNetImage.height()
                sinus = list(map(lambda x: sin(2*pi*x), [x1,y1]))
                sinus2 = list(map(lambda x: sin(2*pi*(x*x)), [x1,y1]))
                input = [float(x1), float(y1)] + sinus + sinus2
                #input = [x1, y1]
                for layer in self.layers:
                    layer.feed(input)
                    input = layer.getY()
                rgb = list(self.layers[len(self.layers)-1].getY())
                rgb = list(map(self.floorRGB, rgb))
                rgb = QColor().fromRgbF(rgb[0], rgb[1], rgb[2])
                rgb = qRgb(rgb.red(), rgb.green(), rgb.blue())
                self.myNetImage.setPixel(x, y, rgb)
        #for i in range(len(self.layers)):
           # print("Layer %s : %s" % (str(i), self.layers[i].getWeights()))
        print("End generation - emit singal >> ID: " + str(QThread.currentThreadId()))
        self.imgGenerated.emit(self.myNetImage)
        print("send weights to save")
        
    def saveWeights(self):
        layersToSend = []
        for layer in self.layers:
            layersToSend.append(layer.getWeights())
        self.sendWeights.emit(self.id, layersToSend)
        
    def setWeights(self, layers):
        for i in range(len(layers)):
            self.layers[i].setWeights(layers[i])
        
    def learnNet(self):
        while(self.doRun):
            #print("\n#### NEXT RUN ####\n")
            (x, y) = (np.random.randint(0, self.image.width()), np.random.randint(0, self.image.height()))
            x1 = x/self.myNetImage.width()
            y1 = y/self.myNetImage.height()
            #print(x, y)
            sinus = list(map(lambda x: sin(2*pi*x), [x1,y1]))
            sinus2 = list(map(lambda x: sin(2*pi*(x*x)), [x1,y1]))
            input = [float(x1), float(y1)] + sinus + sinus2
            #print("Input:" + str(input))
            #input = [x1, y1]
            input = np.array(input)
            
            #print('NPARRAY Inut: ' +  str(input))
            output = np.array(QColor(self.image.pixel(x, y)).getRgbF()[:3])
            #print(self.image.rect())
            #print(self.myNetImage.rect())
            #print(output)
            
            for layer in self.layers:
                layer.feed(input)
                input = layer.getY()
            
            self.layers[len(self.layers)-1].lastLayerFeedBack(output)
            for i in range(len(self.layers)-2, -1, -1):
                #print(i, i+1, len(self.layers))
                self.layers[i].feedBack(self.layers[i + 1])
            for layer in self.layers:
                layer.fixWeights()
                
            rgb = list(self.layers[len(self.layers)-1].getY())
            #rgb = list(map(self.floorRGB, rgb))
            #print("RGBF: " + str(rgb))
            rgb = QColor().fromRgbF(rgb[0], rgb[1], rgb[2])
            #print("RGB" + str(rgb.red())+ str(rgb.green())+ str(rgb.blue()))
            rgb = qRgb(rgb.red(), rgb.green(), rgb.blue())
            self.myNetImage.setPixel(x, y, rgb)
            self.counter += 1
            if self.counter % 1000 == 0:
                self.generatePicture()
                self.sendCounter.emit(str(self.counter))
            if self.counter % 100000 == 0:
                self.saveWeights()
                self.generatePicture2()
                self.saveImage()
                self.sendCounter.emit(str(self.counter))
            
            
    def generatePicture(self):
        self.imgGenerated.emit(self.myNetImage)
        
    def saveImage(self):
        name = self.imgFileName + '{0:05}'.format(self.imgCounter) +'.jpg'
        self.imgCounter += 1
        imagefile = QImageWriter()
        imagefile.setFileName(name)
        imagefile.setFormat("jpg")
        imagefile.setQuality(100)
        imagefile.write(self.myNetImage)
        
    def floorRGB(self, x):
            if x > 1.0:
                return 1.0
            elif x < 0.0:
                return 0.0
            else:
                return x
        
            
    def run(self):
        self.learnNet()
        
#layer = Layer(2,5)
#input = np.array([3,4])
#layer.feed(input)
#print("Layer Output")
#print(layer.getA())
#print("Layer Sigma Output")
#print(layer.getY())
#print("Layer diff")
#print(layer.getdiff())
#print("Layer Weights")
#print(layer.getWeights())
#layer2 = layer
#layer2.lastLayerFeedBack([3, 4, 5,3,3])
#layer.feedBack(layer2)

