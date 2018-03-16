'''
Created on 22 paź 2014

@author: jeedeye
'''
import numpy as np
import time
from multiprocessing import Pool
from numpy.core.fromnumeric import mean


class Perceptron():

    def __init__(self, myDigit, examples, weightsCount):
        #super(Perceptron, self).__init__()
        self.entrances = weightsCount
        self.learnIterations = 500000
        self.eta = 1.0
        self.currentTheta = np.random.random_sample()/10
        self.currentWeights = np.random.random_sample((self.entrances,))/10
        self.currentLifeTime = 0
        self.currentProperClass = 0
        self.recordWeights = {"lifeTime": 0, "properClass": 0, "theta": self.currentTheta, "weights": self.currentWeights}
        self.H = 0.5
        self.sensitivity = 0.0
        self.myDigit = myDigit
        self.examples = examples.copy()
        
    def resetWeights(self):
        self.currentTheta = np.random.random_sample()/10
        self.currentWeights = np.random.random_sample((self.entrances,))/10
        
    def setExamples(self, examples):
        self.examples = examples.copy()
        
    def setWeights(self, newWeights, newTheta):
        self.currentWeights = newWeights
        self.currentTheta = newTheta
        
    def getSensitivity(self):
        allSens = []
        for example in self.examples:
            sens = []
            modifiedExample = example
            isMyClass = -1.0
            if example["digit"] == self.myDigit:
                if example["isProper"]:
                    isMyClass = 1.0
            result = self.classify(example["pixelMap"])
            for i in range(len(example["pixelMap"])):
                modifiedExample["pixelMap"][i] = modifiedExample["pixelMap"][i] + self.H
                modifiedResult = self.classify(modifiedExample["pixelMap"])
                sens.append((modifiedResult - result)/self.H)
            allSens.append(mean(sens))
        self.sensitivity = mean(allSens)
        print("Sensitivity for digit %s: %s" % (self.myDigit, self.sensitivity))
        
    def getWeights(self):
        return self.currentWeights
    
    def getMyDigit(self):
        return self.myDigit
    
    def getTheta(self):
        return self.currentTheta
    
    def classify(self, data):
        #print("self.currentWeights:" + str(self.currentWeights))
        #print("Test Data: " + str(data))
        #print(self.currentWeights * data)
        if self.currentTheta < sum(self.currentWeights * data):
            return 1.0
        else:
            return -1.0
    def isThatYourNumber(self, data):
        if self.classify(data) == 1.0:
            return self.myDigit
        else:
            return -1
    
class PerceptronPool:
    def __init__(self, perceptrons, examples):
        self.numberOfPerceptrons =  len(perceptrons)
        self.examples = examples
        self.perceptrons = perceptrons
        
    ##@profile
    def learnPerc(self):
        pool = Pool(self.numberOfPerceptrons)
        self.newPerceptrons = pool.map(self.learn, self.perceptrons)
        return self.newPerceptrons
    
    
                
    
    def learn(self, perc):
        perc.resetWeights()
        for iter in range(perc.learnIterations):
            #get random example
            randomExample = perc.examples[np.random.randint(0, len(perc.examples))]
            isMyClass = -1.0
            if randomExample["digit"] == perc.myDigit:
                if randomExample["isProper"]:
                    isMyClass = 1.0
            result = perc.classify(randomExample["pixelMap"])
            ERR = isMyClass - result
            if ERR == 0.0:
                perc.currentLifeTime += 1
                
                if perc.currentLifeTime > perc.recordWeights["lifeTime"] and perc.recordWeights["properClass"] < len(perc.examples):
                    #check count of proper classifications
                    currentProperClass = 0
                    for example in perc.examples:
                        isMyClass = -1.0
                        if example["digit"] == perc.myDigit:
                            if example["isProper"]:
                                isMyClass = 1.0
                        result = perc.classify(example["pixelMap"])
                        ERR = isMyClass - result
                        if ERR == 0.0:
                            currentProperClass += 1
                    if currentProperClass >= perc.recordWeights["properClass"]:
                        perc.recordWeights["lifeTime"] = perc.currentLifeTime
                        perc.recordWeights["properClass"] = currentProperClass
                        perc.recordWeights["theta"] = perc.currentTheta
                        perc.recordWeights["weights"] = perc.currentWeights

            else:
                perc.currentLifeTime = 0
                perc.currentTheta -= ERR
                perc.currentWeights += perc.eta * ERR * randomExample["pixelMap"]
                #print("badly classified")
        perc.getSensitivity()
        return perc
          
if __name__ == '__main__':      
    from XMLParser import XMLParser
    print("Start")
    xmlParser = XMLParser()
    examples = xmlParser.getAllExamples()
    perceptrons = [Perceptron(myDigit = i, examples = examples, weightsCount = 6*7) for i in range(10)]
    pool = PerceptronPool(perceptrons, examples)
    pool.learnPerc()
    print("Stop")





