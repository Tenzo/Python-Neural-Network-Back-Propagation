'''
Created on 22 paź 2014

@author: jeedeye
'''

          
    
import numpy as np
import random
import time
from XMLParser import XMLParser
#from profilehooks import profile

class HopfieldNet:
    
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.weights = a = np.zeros(shape=(height * width, height * width))
        self.convExamples = []
        
    def setWeights(self, newWeights):
        self.weights = newWeights
        
        
    def learn(self, examples):
        for example in examples:
            convExample = []
            for row in example:
                convExample.extend(row)
            self.convExamples.append(np.array(convExample))
        for i in range(len(self.convExamples[0])):
            for j in range(len(self.convExamples[0])):
                wij = 0
                if i != j:
                    for example in self.convExamples:
                        wij += example[i] * example[j]
                self.weights[i][j] = wij
        xmlParser = XMLParser()
        xmlParser.setWeights(self.weights)
                        
            
    def associate(self, noisyPicture):
        def flat_for(a, f):
            a = a.reshape(-1)
            for i, v in enumerate(a):
                 a[i] = f(v)
                 
        def sign(x):
            if x < 0:
                return -1
            else:
                return 1

        def chunks(l, n):
            return [l[i:i+n] for i in range(0, len(l), n)]
        
        convPicture = []
        for row in noisyPicture:
            convPicture.extend(row)
        convPicture = np.array(convPicture)
        
        stable = 0
        while(stable < 10):
            #i = random.randint(0, len(convPicture))
            newPicture = np.dot(self.weights, convPicture)
            flat_for(newPicture, sign)
            
            if np.array_equal(newPicture, convPicture):
                stable += 1
                print("Same shape and values")
            else:
                print('Not same shape')
                stable = 0
            convPicture = newPicture 
            
        
        pixelMap = chunks(convPicture, self.height)
        print(pixelMap)
        return pixelMap


if __name__ == '__main__':
    parser = XMLParser()
    examples = parser.getAllExamples()
    hop = HopfieldNet(len(examples[0]), len(examples[0][0]))
    hop.learn(examples)
    #hop.associate(examples[0])
    




