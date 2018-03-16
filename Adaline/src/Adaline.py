'''
Created on 22 paź 2014

@author: jeedeye
'''
import numpy as np
import time
from multiprocessing import Pool
from numpy.core.fromnumeric import mean
from xmlrpc.client import MAXINT


class Adaline():

    def __init__(self, myDigit, examples, weightsCount):
        #super(Adaline, self).__init__()
        self.entrances = weightsCount * 2 + 1
        #print("Adaline init: entrances: " + str(self.entrances))
        self.learnIterations = 100000
        self.eta = 0.0001
        self.currentWeights = np.random.random_sample((self.entrances,))/10
        #print("Adaline init: weights len: " + str(len(self.currentWeights)))
        self.bestResults = { "count" : 0, "weights" : self.currentWeights }
        self.H = 0.5
        self.sensitivity = 0.0
        self.myDigit = myDigit
        self.examples = examples.copy()
        self.errors = []
        
    def resetWeights(self):
        self.currentWeights = np.random.random_sample((self.entrances,))/10
        
    def setExamples(self, examples):
        self.examples = examples.copy()
        
    def setWeights(self, newWeights):
        self.currentWeights = newWeights
        
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
    
    def error(self):
        err = 0.0
        for example in self.examples:
            isMyClass = -1.0
            if example["digit"] == self.myDigit:
                if example["isProper"]:
                    isMyClass = 1.0
            result = self.classify(example["pixelMap"])
            
            err += (isMyClass - result) ** 2
        return err / len(self.examples)
    
    def addFFT(self, data):
        #fft = np.fft.fft(data)
        fft = np.fft.fft(data)
        fft = np.abs(fft) 
        return np.append(data, fft, 0)
        
        
    def classify(self, data):
        ex = self.addFFT(data)
        ex = np.append(ex, [1.0], 0)
        #print("FFT len: " + str(len(ex)) + " Weights len: " + str(len(self.currentWeights)))
        return np.sum(self.currentWeights * ex)

    def isThatYourNumber(self, data):
        if 0.8 < self.classify(data) < 1.2:
            return self.myDigit
        else:
            return -1
    
class AdalinePool:
    def __init__(self, adalines, examples):
        self.numberOfAdalines = len(adalines)
        self.examples = examples
        self.adalines = adalines
        
    def learnPerc(self):
        pool = Pool(self.numberOfAdalines)
        self.newAdalines = pool.map(self.learn, self.adalines)
        return self.newAdalines
    
    
    def learn(self, perc):
        perc.resetWeights()
        currWellClassifiedCount = 0
        for iter in range(perc.learnIterations):
            #get random example
            randomExample = perc.examples[np.random.randint(0, len(perc.examples))]
            isMyClass = -1.0
            if randomExample["digit"] == perc.myDigit:
                if randomExample["isProper"]:
                    isMyClass = 1.0
            result = perc.classify(randomExample["pixelMap"])
            ERR = isMyClass - result
            if abs(ERR) < 0.1:
                currWellClassifiedCount += 1
            else:
                currWellClassifiedCount = 0
            if currWellClassifiedCount > perc.bestResults['count']:
                perc.bestResults['count'] += currWellClassifiedCount
                perc.bestResults['weights'] = perc.currentWeights
                
            ex = perc.addFFT(randomExample["pixelMap"])
            ex = np.append(ex, [1.0], 0)
            
            perc.currentWeights += perc.eta * ERR * ex
            if iter % 100 == 0:
                perc.errors.append(perc.error())
                
        print('Digit: ' + str(perc.myDigit) + ' = ' + str(perc.bestResults['count']))
        perc.currentWeights = perc.bestResults['weights']
        return perc
          
if __name__ == '__main__':      
    from XMLParser import XMLParser
    print("Start")
    xmlParser = XMLParser()
    examples = xmlParser.getAllExamples()
    adalines = [Adaline(myDigit = i, examples = examples, weightsCount = 6*7) for i in range(10)]
    pool = AdalinePool(adalines, examples)
    #pool.learnPerc()
    pool.learn(pool.adalines[0])
    print("Stop")
