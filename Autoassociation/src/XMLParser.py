'''
Created on 22 paź 2014

@author: jeedeye
'''
from xml.dom import minidom
import numpy as np
from Perceptron import Perceptron

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
    print("Only not-C element tree")

class XMLParser:

    def __init__(self, file = '/home/jeedeye/workspace/PerceptronPicture/save.xml'):
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
        
    def getAllPerceptrons(self):
        allPerceptrons = [[{} for j in range(50)] for i in range(50)]
        
        for elem in self.tree.iter(tag='perceptron'):
            if elem.tag == 'perceptron':
                #print(elem.attrib)
                currentRow = int(elem.attrib["row"])
                currentColumn = int(elem.attrib["column"])
                #print(currentRow, currentColumn)
                for child in elem:
                    if child.tag == "theta":
                        theta = float(child.text)
                    if child.tag == "weightMap":
                        weightMapStr = child.text
                        weightMapStr = weightMapStr.split('\n')
                        weightMap = []
                        for row in weightMapStr:
                            weightMap.append(np.array(list(map(float, filter(bool, row.split(';'))))))
                allPerceptrons[currentRow][currentColumn] = (theta, weightMap)            

        return allPerceptrons
    
    #---------------------------------------- def getWeights(self, row, column):
        #------------- perceptrons = self.doc.getElementsByTagName("perceptron")
        #---------------------------------------- for perceptron in perceptrons:
                #------------------- currentRow = perceptron.getAttribute("row")
                #------------- currentColumn = perceptron.getAttribute("column")
                #--- if currentRow == str(row) and currentColumn == str(column):
                    # weightMapStr = perceptron.getElementsByTagName("weightMap")[0].firstChild.data
                    #------------------- weightMapStr = weightMapStr.split('\n')
                    #-------------------------------------------- weightMap = []
                    #---------------------------------- for row in weightMapStr:
                        # weightMap.append(np.array(list(map(float, filter(bool, row.split(';'))))))
                    #------------------------------------------ return weightMap
        #---------------------------------------------------------- return False
                    
    def getTheta(self,  row, column):
        for elem in self.tree.iter('perceptron'):
            if elem.attrib["row"] == str(row) and elem.attrib["column"] == str(column):
                for child in elem:
                    if child.tag == "theta":
                        return float(child.text)
                    
    
    def setWeights(self,  perceptrons):
        for elem in self.tree.iter('perceptron'):
            currentRow = int(elem.attrib["row"])
            currentColumn = int(elem.attrib["column"])
            perc = perceptrons[currentRow][currentColumn]
            for child in elem:
                if child.tag == "theta":
                    child.text = str(perc.getTheta())
                if child.tag == "weightMap":
                    weightMap = perc.getWeights()
                    weightMap =  [';'.join(map(str, row.tolist())) for row in weightMap]
                    weightMap = '\n'.join(weightMap)
                    child.text = weightMap
        self.saveXml()
            
    def addPerceptron(self, row, column, theta, weightMap):
        weightMap =  [';'.join(map(str, row.tolist())) for row in weightMap ]
        weightMap = '\n'.join(weightMap)
        perceptronsNode = self.doc.getElementsByTagName("weights")[0]
        #create example
        newPercNode = self.doc.createElement("perceptron")
        newPercNode.setAttribute("row", str(row))
        newPercNode.setAttribute("column", str(column))
        #create isProper
        newThetaNode = self.doc.createElement("theta")
        thetaText = self.doc.createTextNode(str(theta))
        newThetaNode.appendChild(thetaText)
        #create pixelmap
        newWeightMapNode = self.doc.createElement("weightMap")
        weightMapText = self.doc.createTextNode(str(weightMap))
        newWeightMapNode.appendChild(weightMapText)
        #addChilds
        newPercNode.appendChild(newThetaNode)
        newPercNode.appendChild(newWeightMapNode)
        perceptronsNode.appendChild(newPercNode)
    
    def saveXml(self):
        self.tree.write(self.fileName)
        
    def prettify(self):
        return '\n'.join([line for line in self.doc.toprettyxml(indent=' '*4).split('\n')if line.strip()])
    
    
if __name__ == '__main__':
    parser = XMLParser()
    examples = parser.getAllExamples()
    #perceptrons = parser.getAllPerceptrons()
    print(examples[0][0][0] * -1)
    print(examples[0][0][0])
    
    