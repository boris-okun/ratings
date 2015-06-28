import math
import random
from sample import *

class DistributionDifference :
    def __init__(self, dist1, dist2) :
        self.M = dist1.M - dist2.M
        self.D = dist1.Sigma ** 2 + dist2.Sigma ** 2
    
    def CalcProbability(self) :
        return 0.5 * (1.0 + math.erf(self.M / math.sqrt(2.0 * self.D)))
    
    def CalcError(self, r) :
        return self.CalcProbability() - r
    
    def CalcGradient(self, r) :
        dM1 = math.sqrt(2 / (math.pi * self.D)) * math.exp(-self.M ** 2 / (2.0 * self.D)) * (self.CalcProbability() - r)
        dM2 =  - math.sqrt(2 / (math.pi * self.D)) * math.exp(-self.M ** 2 / (2.0 * self.D)) * (self.CalcProbability() - r)
        dQ1 = - self.M * math.exp(-self.M ** 2 / (2 * self.D)) / math.sqrt(2 * math.pi * self.D ** 3) * (self.CalcProbability() - r)
        dQ2 = dQ1
        return (dM1, dM2, dQ1, dQ2)

class SGDlearn :
    def __init__(self, n, samples) :
        self.Distributions = []
        for i in xrange(n) :
            dist = Distribution(random.random(), random.random())
            self.Distributions.append(dist)
        self.SplitLearnTest(samples)
    
    def SplitLearnTest(self, samples, portion = 0.1) :
        self.Learn = []
        self.Test = []
        for sample in samples :
            if (random.random() > portion) :
                self.Learn.append(sample)
            else :
                self.Test.append(sample)
    
    def CalcError(self, sample) :
        (a, b, r) = sample
        d = DistributionDifference(self.Distributions[a], self.Distributions[b])
        return d.CalcError(r)
    
    def CalcMSE(self, samples) :
        accErr = 0.0
        for sample in samples :
            accErr += self.CalcError(sample) ** 2
        return accErr / len(samples)
    
    def ProcessSample(self, sample, alpha) :
         (a, b, r) = sample
         d = DistributionDifference(self.Distributions[a], self.Distributions[b])
         (dM1, dM2, dD1, dD2) = d.CalcGradient(r)
         self.Distributions[a].M -= alpha * dM1
         self.Distributions[b].M -= alpha * dM2
         self.Distributions[a].Sigma = math.sqrt(max(0.0001, self.Distributions[a].Sigma ** 2 - alpha * dD1))
         self.Distributions[b].Sigma = math.sqrt(max(0.0001, self.Distributions[b].Sigma ** 2 - alpha * dD2))
    
    def Iteration(self, alpha) :
        random.shuffle(self.Learn)
        for sample in self.Learn :
            self.ProcessSample(sample, alpha)
        learnMSE = self.CalcMSE(self.Learn)
        testMSE = self.CalcMSE(self.Test)
        print ("LearnMSE = %f\nTestMSE = %f" % (learnMSE, testMSE))
        return testMSE
    
    def RunLearn(self, alpha, threshold) :
        testMSE = self.CalcMSE(self.Test)
        print "Initial Test MSE = %f" % testMSE
        newTestMSE = 0
        index = 0
        while (testMSE - newTestMSE > threshold) :
            index += 1
            print "Iteration %d" % index
            if (newTestMSE > 0) :
                testMSE = newTestMSE
            newTestMSE = self.Iteration(alpha)
        return newTestMSE
    
def Test(distNumber, samplesNumber, delta,  alpha, threshold) :
    distributions = GenerateDistributions(distNumber)
    testDistributions = GenerateDistributions(distNumber)
    samples = GeneratePairs(samplesNumber, distributions, delta)
    learner = SGDlearn(distNumber, samples)
    learner.RunLearn(alpha, threshold)
    print "Sample random distributions :"
    CheckAnswer(distributions, testDistributions)
    print "Learned distributions :"
    CheckAnswer(distributions, learner.Distributions)
    
def MyParamsRun() :
    teams = RunRating('data/results_20150628', 10, 50, 100, 0.01, 0.001)
