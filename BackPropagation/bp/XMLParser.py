'''
Created on 22 paź 2014

@author: jeedeye
'''
from xml.dom import minidom
import numpy as np

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    print("Only not-C element tree")
from PyQt5.QtCore import *
class XMLParser(QObject):

    def __init__(self, file = '/home/jeedeye/workspace/BackPropagation/bp/save.xml'):
        self.fileName = file
        self.tree = ET.ElementTree(file=self.fileName)
        
    def getImgCounter(self, netId):
        for elem in self.tree.iter(tag='net'):
            if elem.tag == 'net':
                #print(elem.attrib)
                currentId = int(elem.attrib["id"])
                #print(currentRow, currentColumn)
                if currentId == netId:
                    for child in elem:
                        if child.tag == "netCounter":
                            return int(child.text)
        
    def getNet(self, netId):
        layers = []
        for elem in self.tree.iter(tag='net'):
            if elem.tag == 'net':
                #print(elem.attrib)
                currentId = int(elem.attrib["id"])
                #print(currentRow, currentColumn)
                if currentId == netId:
                    for child in elem:
                        if child.tag == "layer":
                            layerNo = int(child.attrib["no"])
                            weightMapStr = child.text
                            weightMapStr = weightMapStr.split('\n')
                            weightMap = []
                            for row in weightMapStr:
                                nums = list(map(float, filter(bool, row.split(';'))))
                                #print(nums)
                                weightMap.append(nums)
                            layers.append(np.array(weightMap))
        return layers
                    
                    
    @pyqtSlot(int, list)
    def setNet(self, netId, layers):
        for elem in self.tree.iter('net'):
            if elem.tag == 'net':
                currentId = int(elem.attrib["id"])
                if currentId == netId:
                    for child in elem:
                        if child.tag == "layer":
                            index = int(child.attrib["no"])
                            print("Index:" +str(index))
                            currentLayer = layers[index]
                            print("Layer len: " + str(len(currentLayer)))
                            #print(currentLayer[:, 0].tolist())
                            currentLayer =  [';'.join(map(str, currentLayer[i,:])) for i in range(len(currentLayer))]
                            currentLayer = '\n'.join(currentLayer)
                            child.text = currentLayer
        print("XMLParser: Saving weights")
        self.saveXml()
        
    @pyqtSlot(int, int)
    def setImgCounter(self, netId, imgCounter):
        for elem in self.tree.iter('net'):
            if elem.tag == 'net':
                currentId = int(elem.attrib["id"])
                if currentId == netId:
                    for child in elem:
                        if child.tag == "netCounter":
                            child.text = str(imgCounter)
        print("XMLParser: Saving counter")
        self.saveXml()
            
    
    def saveXml(self):
        self.tree.write(self.fileName)
        
    def prettify(self):
        return '\n'.join([line for line in self.doc.toprettyxml(indent=' '*4).split('\n')if line.strip()])
    
    
if __name__ == '__main__':
    parser = XMLParser()
    currCounter = parser.getImgCounter(0)
    print(currCounter)

    
    
    