# this program runs simulations of various sketches for many runs to find out variance
# all sketchs at least has name, color, update, record

import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
import time
import pickle


class LLSketch:
    def __init__(self, pm, pq, pN, pcolor=None):
        self.name = 'LL__'
        if pcolor is None:
            self.color = 'red'
        self.m = pm
        self.q = pq
        self.states = np.zeros(pm, dtype=int)
        self.Mtg = 0 # martingale estimator
        self.a = pm # m times the remaining area
        self.MtgHist = np.zeros(pN)
        #self.LogHist = np.zeros((pN, pm+4))
        self.ShortLogHist = np.zeros((pN, 4))

    def update(self, c, k, t):
        if k > self.states[c]:
            self.Mtg += self.m / self.a
            self.a += np.power(1/self.q, k) - np.power(1/self.q, self.states[c])
            self.states[c] = k
        self.record(c, k, t)

    def record(self, c, k, t):
        self.MtgHist[t] = self.Mtg
        #self.LogHist[t] = np.hstack((self.Mtg, self.a, c, k, self.states))
        self.ShortLogHist[t] = np.hstack((self.Mtg, self.a, c, k))


class ThrsSketch:
    def __init__(self, pm, pq, pUpbd, pN, pcolor=None):
        self.name = 'Thrs'
        if pcolor is None:
            self.color = 'green'
        self.m = pm
        self.q = pq
        self.upbd = pUpbd # upper bound
        self.states = np.zeros(self.m, dtype=int)
        self.Min = 0
        self.Mtg = 0
        self.a = pm # m times the remaining area
        self.DeadList = np.zeros(pm, dtype=int) # recording the death time, 0 for alive
        self.DeadNum = 0
        #self.LogHist = np.zeros((pN, self.m+6))
        self.ShortLogHist = np.zeros((pN, 6))
        self.MtgHist = np.zeros(pN)
        self.DeadNumHist = np.zeros(pN, dtype=int)

    def update(self, c, k, t):
        if 0 <= self.states[c] < k:
            if k - self.Min > self.upbd:
                self.DeadList[c] = t
                self.DeadNum += 1
                self.Mtg += self.m / self.a
                self.a -= np.power(1/self.q, self.states[c])
                self.states[c] = -k
            else:
                self.Mtg += self.m / self.a
                self.a += np.power(1/self.q, k) - np.power(1/self.q, self.states[c])
                Oldstate = self.states[c]
                self.states[c] = k
                if Oldstate == self.Min:
                    self.Min = np.min(np.where(self.states >= 0, self.states, InftyLL))
        self.record(c, k, t)

    def record(self, c, k, t):
        self.MtgHist[t] = self.Mtg
        self.DeadNumHist[t] = self.DeadNum
        #self.LogHist[t] = np.hstack((self.Mtg, self.a, self.Min, self.DeadNum, c, k, self.states))
        self.ShortLogHist[t] = np.hstack((self.Mtg, self.a, self.Min, self.DeadNum, c, k))


class CdbkSketch:
    def __init__(self, pm, pq, pCodebook, pN, pcolor=None):
        self.name = 'Cdbk'
        if pcolor is None:
            self.color = 'blue'
        self._m = int(pm/3)
        self.m = 3 * self._m
        self.q = pq
        self.Codebook = pCodebook
        self.states = np.zeros(self.m, dtype=int)
        self.Mtg = 0
        self.LogMtg = 0
        self.a = self.m  # m times the remaining area
        self.DeadList = np.zeros(self._m, dtype=int)  # recording the death time, 0 for alive
        self.DeadNum = 0
        self.DeadFlag = np.ones(self.m, dtype=int) # 1 for alive, 0 for dead
        self.MtgHist = np.zeros(pN)
        self.DeadNumHist = np.zeros(pN, dtype=int)
        #self.LogHist = np.zeros((pN, self.m+6))
        self.ShortLogHist = np.zeros((pN, 6))

    def getTrplt(self, _c):
        return (self.states[3 * _c] - self.LogMtg,
                self.states[3 * _c + 1] - self.LogMtg, self.states[3 * _c + 2] - self.LogMtg)

    def update(self, c, k, t):
        _c = int(c/3)
        if k > self.states[c] and self.DeadFlag[c] == 1:
            self.states[c] = k
            Trplt = self.getTrplt(_c)
            if Trplt not in self.Codebook:
                self.DeadFlag[(3*_c):(3*_c+3)] = 0
                self.DeadNum += 3
                self.DeadList = t
                self.states[(3*_c):(3*_c+3)] *= -1
            self.Mtg += self.m / self.a
            NewLogMtg = max(int(math.log(self.Mtg / self.m, self.q)), 0)

            if NewLogMtg != self.LogMtg:
                diff = NewLogMtg - self.LogMtg
                self.LogMtg = NewLogMtg
                for _c in range(self._m):
                    Trplt = self.getTrplt(_c)
                    if Trplt not in self.Codebook and self.DeadFlag[_c] == 1:
                        self.states[(3*_c):(3*_c+3)] += diff

            self.a = np.dot(np.power(1/self.q, self.states), self.DeadFlag)
        self.record(c, k, t)

    def record(self, c, k, t):
        self.MtgHist[t] = self.Mtg
        self.DeadNumHist[t] = self.DeadNum
        #self.LogHist[t] = np.hstack((self.Mtg, self.a, self.LogMtg, self.DeadNum, c, k, self.states))
        self.ShortLogHist[t] = np.hstack((self.Mtg, self.a, self.LogMtg, self.DeadNum, c, k))


def myplot(mSketches, title, pN, pr):
    fig = plt.figure(num=2, figsize=(15, 8), dpi=80)
    ax1 = fig.add_subplot(1, 2, 1)
    ax2 = fig.add_subplot(1, 2, 2)
    mx = range(pN)
    for msketch in mSketches:
        if hasattr(msketch, 'MtgHist'):
            ax1.plot(mx, msketch.MtgHist, color=msketch.color)
    ax1.plot(mx, mx, color='black')
    plt.title(title)
    for msketch in mSketches:
        if hasattr(msketch, 'DeadNumHist'):
            ax2.plot(mx, msketch.DeadNumHist, color=msketch.color)
    plt.savefig("figs/" + "Type3-" + getTimeString() + "-(" + str(pr) + ").png")
    plt.show()


def savehist(TTLHist, title):
    TTLHistDf = pd.DataFrame(TTLHist)
    TTLHistDf.to_csv("TTLHist/" + title + getTimeString() +".csv")


def getTimeString():
    return time.strftime(time.strftime("%m_%d_%H_%M_%S"))


m = 300
q = 2.0
N = 500000
Upbd = 5
Size = 511
InftyLL = 1000
Rounds = 3
TraceTTLHist = True
TraceTTLHistFreq = 1
TraceMtgPlot = True
TraceMtgPlotFreq = 1
TraceMtgRelVar = False

cdbkfile = 'codebooks/Codebook-' + str(Size) + '.pkl'
with open(cdbkfile, "rb") as file:
    Codebook = pickle.load(file)

LLMtgVar = np.zeros(N)
ThrsMtgVar = np.zeros(N)
CdbkMtgVar = np.zeros(N)
x = np.arange(N) + 1

for r in range(Rounds):
    LL = LLSketch(m, q, N)
    Thrs = ThrsSketch(m, q, Upbd, N)
    Cdbk = CdbkSketch(m, q, Codebook, N)
    #Sketches = [LL, Thrs, Cdbk]
    Sketches = [LL, Thrs]
    for t in range(N):
        c = np.random.randint(0, m)
        k = np.random.geometric(1/q)
        for sketch in Sketches:
            sketch.update(c, k, t)

    if TraceMtgPlot and r % TraceMtgPlotFreq == 0:
        plotTitle = 'm=%d; N=%d; Upbd=%d; CdbkSize=%d, round %d' % (m, N, Upbd, Size, r)
        myplot(Sketches, plotTitle, N, r)

    if TraceTTLHist and r % TraceTTLHistFreq == 0:
        # trace total history with a frequency
        for sketch in Sketches:
            #savehist(sketch.LogHist, 'TTHHist_' + sketch.name + '_')
            savehist(sketch.ShortLogHist, 'TTHHist_' + sketch.name + '_')

    if TraceMtgRelVar:
        LLMtgVar += np.square(np.divide(LL.MtgHist, x) - 1)
        ThrsMtgVar += np.square(np.divide(Thrs.MtgHist, x) - 1)
        #CdbkMtgVar += np.square(np.divide(Cdbk.MtgHist, x) - 1)

if TraceMtgRelVar:
    LLMtgVar /= Rounds
    ThrsMtgVar /= Rounds
    #CdbkMtgVar /= Rounds

    plt.plot(x, LLMtgVar, color='red')
    plt.plot(x, ThrsMtgVar, color='green')
    #plt.plot(x, CdbkMtgVar, color='blue')
    #plt.title("m=%d, N=%d, Upbd=%d, CdbkSize=%d, %d rounds" % (m, N, Upbd, Size, Rounds))
    plt.title("m=%d, N=%d, Upbd=%d, %d rounds" % (m, N, Upbd, Rounds))
    plt.savefig("figs/" + "Type4-" + getTimeString() + ".png")
    plt.show()
