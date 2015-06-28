import random
import math

class Distribution :
    def __init__(self, m, s) :
        self.M = m
        self.Sigma = s
    
    def Generate(self) :
        return random.gauss(self.M, self.Sigma)

def GenerateDistributions(n, maxSigma = 1) :
    result = []
    for i in xrange(n) :
        dist = Distribution(random.random(), random.random() * maxSigma)
        result.append(dist)
    return result

def GeneratePairs(n, distributions, delta) :
    result = []
    for i in xrange(n) :
        a = int(random.random() * len(distributions))
        b = int(random.random() * (len(distributions) - 1))
        if (a <= b) : b += 1
        r1 = distributions[a].Generate()
        r2 = distributions[b].Generate()
        if (r1 > r2 + delta) : r = 1.
        elif (r2 > r1 + delta) : r = 0.
        else : r = 0.5
        result.append((a,b,r))
    return result

def CheckAnswer(distributions, guessedDistributions) :
    if len(distributions) != len(guessedDistributions) :
        raise ValueError('Different length of input arrays')
    normalizedGuessedDistributions = NormalizeDistributions(guessedDistributions)
    accMError = 0.
    accSError = 0.
    accM = 0.
    accS = 0.
    for i in xrange(len(distributions)) :
        accMError += (distributions[i].M - normalizedGuessedDistributions[i].M) ** 2
        accSError += (distributions[i].Sigma - normalizedGuessedDistributions[i].Sigma) ** 2
        accM += distributions[i].M ** 2
        accS += distributions[i].Sigma ** 2
    mError = math.sqrt(accMError) / len(distributions)
    sError = math.sqrt(accSError) / len(distributions)
    print "MSError for M = %f\nMSError for Sigma = %f" % (mError, sError)
    print "MSError / MSValue for M = %f\nMSError / MSValue for Sigma = %f" % (math.sqrt(accMError) / math.sqrt(accM) , math.sqrt(accSError) / math.sqrt(accS))
    return (mError, sError)

def NormalizeDistributions(distributions) :
    maxM = max([dist.M for dist in distributions])
    minM = min([dist.M for dist in distributions])
    maxSigma = max([dist.Sigma for dist in distributions])
    result = []
    for dist in distributions :
        result.append(Distribution((dist.M - minM)/(maxM - minM), dist.Sigma / maxSigma))
    return result      
