'''
Created on 22 lis 2014

@author: jeedeye
'''
import time
from Perceptron import Perceptron, PerceptronPool
from XMLParser import XMLParser

def learnPerceptrons():
    MULTI = False
    HEIGHT = 50
    WIDTH = 50
    ENTRANCES = HEIGHT * WIDTH
    xmlParser = XMLParser()
    examples = xmlParser.getAllExamples()
    print("Got examples")
    perceptrons = []
    for i in range(HEIGHT):
        row = []
        for j in range(WIDTH):
            perc = Perceptron(i,j, examples, ENTRANCES)
            row.append(perc)
        perceptrons.append(row)
    print("Created perceptrons")
    beforeTime = time.process_time()
    if MULTI:
        print("Created pool")
        percPool = PerceptronPool(perceptrons, examples)
        perceptrons = percPool.learnPerc()
    else:
        for row in perceptrons:
            print("processing row %s" % str(perceptrons.index(row)))
            for perc in row:
                perc.learn()
    learnTime = elapsed_time = time.process_time() - beforeTime
    print("LearnTime : " + str(learnTime))
    
    xmlParser.setWeights(perceptrons)
        
        
if __name__ == '__main__':   
    print("start")   
    learnPerceptrons()
    print("stop")
