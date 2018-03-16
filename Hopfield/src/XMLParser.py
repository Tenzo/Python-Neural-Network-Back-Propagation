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

class XMLParser:

    def __init__(self, file = '/home/jeedeye/workspace/Hopfield/src/save.xml'):
        self.fileName = file
        self.tree = ET.ElementTree(file=self.fileName)
        
    def getAllExamples(self):
        allExamples = []
        for event, elem in ET.iterparse(self.fileName):
            if event == 'end':
                if elem.tag == 'pixelMap':
                    pixelMapStr = elem.text
                    pixelMapStr = pixelMapStr.split('\n')
                    pixelMap = []
                    for row in pixelMapStr:
                        pixelMap.append(np.array(list(map(float, filter(bool, row.split(';'))))))
                    allExamples.append(pixelMap)
            elem.clear() # discard the element
        return allExamples
                #print("digit:%s, pixelMap: %s isProper: %s" % (digit, pixelMap, isProper))
    
    def addExample(self, pixelMap):
        pixelMap =  [';'.join(map(str, row.tolist())) for row in pixelMap ]
        pixelMap = '\n'.join(pixelMap)
        for elem in self.tree.iter('examples'):
                    newExample = ET.SubElement(elem, 'example')
                    newPixelMap = ET.SubElement(newExample, 'pixelMap')
                    newPixelMap.text = pixelMap
        self.saveXml()
        
    def getWeights(self):
        weightMap = np.array([])
        for elem in self.tree.iter(tag='hopfield'):
            if elem.tag == 'hopfield':
                weightMapStr = elem.text
                weightMapStr = weightMapStr.split('\n')
                weightMap = []
                for row in weightMapStr:
                    weightMap.append(np.array(list(map(float, filter(bool, row.split(';'))))))
                           

        return weightMap
    
                    
    
    def setWeights(self,  weights):
        for elem in self.tree.iter('hopfield'):
                weightMap = weights
                weightMap =  [';'.join(map(str, row.tolist())) for row in weightMap]
                weightMap = '\n'.join(weightMap)
                elem.text = weightMap
        self.saveXml()
    
    def saveXml(self):
        self.tree.write(self.fileName)
        
    def prettify(self):
        return '\n'.join([line for line in self.doc.toprettyxml(indent=' '*4).split('\n')if line.strip()])
    
    
if __name__ == '__main__':
    parser = XMLParser()
    examples = parser.getAllExamples()
    #hopfields = parser.getAllhopfields()
    weights = parser.getWeights()
    print(weights)
    parser.setWeights(np.array([[3,4,4],[3,5,6]]))
    weights = parser.getWeights()
    print(weights)
    parser.addExample(([np.array([2,4,5,3,2]),np.array([23,5,6,34,5,5]),np.array([34,5,53,34,5,56])]))
    examples = parser.getAllExamples()
    print(examples)
    
    