'''
Created on 22 paź 2014

@author: jeedeye
'''
from xml.dom import minidom
import numpy as np
class XMLParser:

    def __init__(self, file = '/home/jeedeye/workspace/PerceptronNumbers/save.xml'):
        self.fileName = file
        self.doc = minidom.parse(self.fileName)

    def getAllExamples(self):
        allExamples = []
        examplesNode = self.doc.getElementsByTagName("example")
        for exampleNode in examplesNode:
                digit = int(exampleNode.getAttribute("digit"))
                pixelMap = exampleNode.getElementsByTagName("pixelMap")[0]
                pixelMap = np.array(list(map(float, filter(bool, pixelMap.firstChild.data.split(';')))))
                isProper = 'True' == exampleNode.getElementsByTagName("isProper")[0].firstChild.data
                allExamples.append({'digit': digit, "isProper" : isProper, "pixelMap" : pixelMap})
        return allExamples
                #print("digit:%s, pixelMap: %s isProper: %s" % (digit, pixelMap, isProper))
    
    def addExample(self, digit, pixelMap, isProper):
        pixelMap = ';'.join(map(str,pixelMap.tolist()))
        
        exampleNode = self.doc.getElementsByTagName("examples")[0]
        #create example
        newExampleNode = self.doc.createElement("example")
        newExampleNode.setAttribute("digit", str(digit))
        #create isProper
        newIsProperNode = self.doc.createElement("isProper")
        isProperText = self.doc.createTextNode(str(isProper))
        newIsProperNode.appendChild(isProperText)
        #create pixelmap
        newPixelMapNode = self.doc.createElement("pixelMap")
        pixelMapText = self.doc.createTextNode(str(pixelMap))
        newPixelMapNode.appendChild(pixelMapText)
        #addChilds
        newExampleNode.appendChild(newIsProperNode)
        newExampleNode.appendChild(newPixelMapNode)
        exampleNode.appendChild(newExampleNode)
    
        self.saveXml()
    
    def getWeights(self, digit):
        perceptrons = self.doc.getElementsByTagName("perceptron")
        for perceptron in perceptrons:
                currentdigit = perceptron.getAttribute("digit")
                if currentdigit == str(digit):
                    weightMap = perceptron.getElementsByTagName("weightMap")[0]
                    weightMap = np.array(list(map(float, filter(bool, weightMap.firstChild.data.split(';')))))
                    return weightMap
        return False
                    
    def getTheta(self, digit):
        perceptrons = self.doc.getElementsByTagName("perceptron")
        for perceptron in perceptrons:
                currentdigit = perceptron.getAttribute("digit")
                if currentdigit == str(digit):
                    return float(perceptron.getElementsByTagName("theta")[0].firstChild.data)
        return False
                    
    
    def setWeights(self, digit, theta, weightMap):
        weightMap = ';'.join(map(str, weightMap.tolist()))
        perceptronsNode = self.doc.getElementsByTagName("perceptron")
        for perceptronNode in perceptronsNode:
            if perceptronNode.getAttribute('digit') == str(digit):
                weightNode = perceptronNode.getElementsByTagName("weightMap")[0]
                weightNode.firstChild.data = weightMap
                
                thetaNode = perceptronNode.getElementsByTagName("theta")[0]
                thetaNode.firstChild.data = str(theta)
        
            
    def saveXml(self):
        file = open(self.fileName, "w")
        file.write(self.prettify())
        file.close()
        
    def prettify(self):
        return '\n'.join([line for line in self.doc.toprettyxml(indent=' '*4).split('\n')if line.strip()])
    