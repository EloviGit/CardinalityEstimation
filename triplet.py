# this program trys to get a codebook
# that is, find the most frequent triplets

import numpy as np
import pandas as pd
import pickle

q = 2.0
m = 3

Range = 12
Shift = 3
Size = 511
# codebook 511: from -3 to 8
# codbook 1023: from -3 to 8
# codebook 2047: from -5 to 10.


def F1(i):
    return np.exp(-1/(2**(i+1))) - np.exp(-1/(2**i))

def CodebookGen(Range, Shift, Size, evalf):
    Square = Range * Range
    Cube = Square * Range
    ProbMap = np.zeros(Cube) # probMap[Sq*i+R*j+k] stores the prob for i-S, j-S, k-S
    SingCordMap = np.zeros(Range) # SingCordMap[i] stores for i - S
    for i in range(Range):
        SingCordMap[i] = evalf(i - Shift)
    print(SingCordMap)
    for s in range(Cube):
        i, j, k = NtoT(s, Range)
        ProbMap[s] = SingCordMap[i] * SingCordMap[j] * SingCordMap[k]
    ind = np.argsort(ProbMap)
    codebook = [NtoT(ind[-i], Range, Shift) for i in range(1, Size + 1)]
    nonneg = [codebook[i] for i in range(Size) if codebook[i][0] >= 0 and codebook[i][1] >= 0 and codebook[i][2] >= 0]
    return codebook, nonneg

def TtoN(i, j, k, Range, Shift=0):
    # tuple to number
    return (i+Shift)*Range*Range + (j+Shift)*Range + (k+Shift)

def NtoT(s, Range, Shift=0):
    # number to tuple
    Square = Range*Range
    return int(s/Square) - Shift, ((int(s/Range)) % Range) - Shift, (s % Range) - Shift


Codebook, Nonneg = CodebookGen(Range, Shift, Size, F1)
filestr = 'codebooks/Codebook-' + str(Size)

print(Codebook)
print(Nonneg)

#with open(filestr + '.pkl', "wb") as file:
#    pickle.dump(Codebook, file, True)
#
#Codebookdf = pd.DataFrame(Codebook)
#Codebookdf.to_csv(filestr + '.csv')
#Nonnegdf = pd.DataFrame(Nonneg)
#Nonnegdf.to_csv(filestr + '-nonneg.csv')
