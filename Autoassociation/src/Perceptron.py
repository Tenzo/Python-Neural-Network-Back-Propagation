'''
Created on 22 paź 2014

@author: jeedeye
'''
import numpy as np
import time
#from profilehooks import profile
from multiprocessing import Pool



class Perceptron():

    def __init__(self, row, column , examples, weightsCount):
        #super(Perceptron, self).__init__()
        self.entrances = weightsCount
        self.learnIterations = 150
        self.eta = 1.0
        self.currentTheta = np.random.random_sample()/10
        self.currentWeights = []
        for i in range(50):
            randomRow = np.random.uniform(-1, 1, size=50)/10
            self.currentWeights.append(randomRow)
        self.currentLifeTime = 0
        self.currentProperClass = 0
        self.recordWeights = {"lifeTime": 0, "properClass": 0, "theta": self.currentTheta, "weights": self.currentWeights}
        
        self.row = row
        self.column = column
        self.examples = examples.copy()
        
    def resetWeights(self):
        self.currentWeights = []
        for i in range(50):
            randomRow = np.random.uniform(-1, 1, size=50)/10
            self.currentWeights.append(randomRow)
        
    def setExamples(self, examples):
        self.examples = examples.copy()
        
    def setWeights(self, newWeights, newTheta):
        self.currentWeights = newWeights
        self.currentTheta = newTheta
        
        
    def getWeights(self):
        return self.currentWeights
    
    def getRow(self):
        return self.row
    
    def getColumn(self):
        return self.column
    
    def getTheta(self):
        return self.currentTheta
    
    def classify(self, data):
        #print("self.currentWeights:" + str(self.currentWeights))
        #print("Test Data: " + str(data))
        #print(self.currentWeights * data)
        #print(self.currentWeights[0].shape)
        #print(data[0].shape)
        if self.currentTheta < sum([np.dot(self.currentWeights[i], data[i]) for i in range(len(data)) ]):
            return 1.0
        else:
            return -1.0

    def learn(self):
        self.resetWeights()
        for iter in range(self.learnIterations):
            #get random example
            randomExample = self.examples[np.random.randint(0, len(self.examples))]
            isMyClass = randomExample[self.getRow()][self.getColumn()]
            
            #get some soil
            #for k in range(np.random.randint(0, 10)):
            #    i = np.random.randint(0, len(randomExample))
            #    j = np.random.randint(0, len(randomExample))
            #    randomExample[i][j] *= -1
            
            result = self.classify(randomExample)
            ERR = isMyClass - result
            if ERR == 0.0:
                self.currentLifeTime += 1
                
                if self.currentLifeTime > self.recordWeights["lifeTime"] and self.recordWeights["properClass"] < len(self.examples):
                    #check count of proper classifications
                    currentProperClass = 0
                    for example in self.examples:
                        isMyClass = example[self.getRow()][self.getColumn()]
                        result = self.classify(example)
                        ERR = isMyClass - result
                        if ERR == 0.0:
                            currentProperClass += 1
                    if currentProperClass >= self.recordWeights["properClass"]:
                        self.recordWeights["lifeTime"] = self.currentLifeTime
                        self.recordWeights["properClass"] = currentProperClass
                        self.recordWeights["theta"] = self.currentTheta
                        self.recordWeights["weights"] = self.currentWeights
                        #print("Better Weights")

            else:
                self.currentLifeTime = 0
                self.currentTheta -= ERR
                multiplyBy = self.eta * ERR
                for row in range(len(self.currentWeights)):
                    self.currentWeights[row] += multiplyBy * randomExample[row]
    
class PerceptronPool:
    def __init__(self, perceptrons, examples):
        self.numberOfPerceptrons =  5
        self.examples = examples
        self.perceptrons = perceptrons
        
    ##@profile
    def learnPerc(self):
        pool = Pool(self.numberOfPerceptrons)
        self.newPerceptrons = []
        for row in self.perceptrons:
            self.newPerceptrons.append(pool.map(self.learn, row))
            print("Row %s is done" % str(self.perceptrons.index(row)))
        return self.newPerceptrons
    
    def learn(self, perc):
        perc.resetWeights()
        for iter in range(perc.learnIterations):
            #get random example
            randomExample = perc.examples[np.random.randint(0, len(perc.examples))]
            isMyClass = randomExample[perc.getRow()][perc.getColumn()]
            result = perc.classify(randomExample)
            ERR = isMyClass - result
            if ERR == 0.0:
                perc.currentLifeTime += 1
                
                if perc.currentLifeTime > perc.recordWeights["lifeTime"] and perc.recordWeights["properClass"] < len(perc.examples):
                    #check count of proper classifications
                    currentProperClass = 0
                    for example in perc.examples:
                        isMyClass = example[perc.getRow()][perc.getColumn()]
                        result = perc.classify(example)
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
                multiplyBy = perc.eta * ERR
                for row in range(len(perc.currentWeights)):
                    perc.currentWeights[row] += multiplyBy * randomExample[row]
                #print("badly classified")
                
        return perc
    





