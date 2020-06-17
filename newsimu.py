# this program runs simulations for various sketches and the code is arranged nicely

import numpy as np
import math
import pandas as pd
import matplotlib.pyplot as plt
import time
import pickle
import tqdm

VersionStr = "T5"
Infty = 32 # to us, values above 32 is a state not possible to appear in LL simulation. in simulation not even 16
MaxChange = 16 # I believe there should not be more than 16 changes happening on one counter. in simulation not even 13.


class Sketch:
    def __init__(self, pm, pq, pN, pcolor, pname, psnapshotLen=5, prunMaxChange=MaxChange):
        self.name = pname
        self.color = pcolor
        self.m = pm
        self.q = pq
        self.N = pN
        self.states = np.zeros(pm, dtype=int)
        self.Mtg = 0
        self.a = pm

        self.runningHist = np.zeros((pm, 2*prunMaxChange), dtype=int)
        self.runningColStr = ["time"+str(int(i/2)) if i % 2 == 0 else "value"+str(int(i/2))
                              for i in range(2*prunMaxChange)]
        self.runningHist_inx = np.zeros(pm, dtype=int)
        self.runningHistdf = pd.DataFrame()

        self.snapshotLen = psnapshotLen
        self.snapshotColStr = ["t", "c", "k", "Mtg", "a"]
        self.snapshot = np.zeros(self.snapshotLen)
        self.snapshotHist = np.zeros((MaxChange*pm, self.snapshotLen))
        self.snapshotHist_inx = 0
        self.snapshotHistdf = pd.DataFrame()

    def update(self, c, k, t):
        # if updated, return True; not updated, return False
        # remember to update the snapshot
        # and return a list of coords to updated
        return True, []

    def record(self, cList, t):
        for c in cList:
            runningHist_inx_c = self.runningHist_inx[c]
            self.runningHist[c][runningHist_inx_c:runningHist_inx_c+2] = (t, self.states[c])
            self.runningHist_inx[c] += 2
        self.snapshotHist[self.snapshotHist_inx] = self.snapshot
        self.snapshotHist_inx += 1

    def savehist(self, mode="excel"):
        self.runningHistdf = pd.DataFrame(self.runningHist, columns=self.runningColStr)
        self.snapshotHistdf = pd.DataFrame(self.snapshotHist, columns=self.snapshotColStr)
        if mode == "excel":
            sWriter = pd.ExcelWriter("TTLHist/"+VersionStr+"_"+self.name+"_"+getTimeString()+".xlsx")
            self.runningHistdf.to_excel(sWriter, "running")
            self.snapshotHistdf.to_excel(sWriter, "snapshot")
            sWriter.save()
        elif mode == "csv":
            self.runningHistdf.to_csv("TTLHist/"+VersionStr+"_"+self.name+"_running_"+getTimeString()+".csv")
            self.snapshotHistdf.to_csv("TTLHist/"+VersionStr+"_"+self.name+"_snapshots_"+getTimeString()+".csv")


class LLSketch(Sketch):
    def __init__(self, pm, pq, pN, pcolor="red", pname="LL"):
        super(LLSketch, self).__init__(pm, pq, pN, pcolor, pname)

    def update(self, c, k, t):
        if k > self.states[c]:
            self.Mtg += self.m / self.a
            self.a += np.power(self.q, -k) - np.power(self.q, -self.states[c])
            self.states[c] = k
            self.snapshot = np.array([t, c, k, self.Mtg, self.a])
            return True, [c]
        else:
            return False, []


class ThrsSketch(Sketch):
    def __init__(self, pm, pq, pN, pUpbd, pcolor='green', pname="Thrs"):
        super(ThrsSketch, self).__init__(pm, pq, pN, pcolor, pname, 7)
        self.upbd = pUpbd
        self.DeadFlags = np.zeros(pm, dtype=int) + 1 # 1 for alive, 0 for dead
        self.Min = 0
        self.DeadNum = 0
        self.snapshotColStr += ["Min", "DeadNum"]

    def update(self, c, k, t):
        if k > self.states[c] and self.DeadFlags[c] == 1:
            if k - self.Min > self.upbd:
                # this counter dead
                self.DeadNum += 1
                self.DeadFlags[c] = 0
                self.states[c] = Infty
            else:
                self.states[c] = k
            self.Mtg += self.m / self.a
            self.a = np.dot(np.power(self.q, -self.states), self.DeadFlags)
            self.Min = np.min(self.states)
            self.snapshot = np.array([t, c, k, self.Mtg, self.a, self.Min, self.DeadNum])
            return True, [c]
        else:
            return False, []


class CdbkSketch(Sketch):
    def __init__(self, pm, pq, pN, pCodebook, pcolor="blue", pname="Cdbk"):
        _m = int(pm/3)
        m = _m * 3
        super(CdbkSketch, self).__init__(m, pq, pN, pcolor, pname, 7, 3*MaxChange)
        self.Codebook = pCodebook
        self.DeadFlags = np.zeros(pm, dtype=int) + 1
        self._m = _m
        self.DeadNum = 0
        self.LogMtg = 0
        self.snapshotColStr += ["LogMtg", "DeadNum"]

    def update(self, c, k, t):
        if k > self.states[c] and self.DeadFlags[c] == 1:
            _c = int(c/3)
            cList = [3*_c, 3*_c+1, 3*_c+2]
            self.states[c] = k
            triple = tuple(self.states[3*_c : 3*_c+3] - self.LogMtg)
            if triple not in self.Codebook:
                self.DeadFlags[3*_c:3*_c+3] = 0
                self.DeadNum += 3
                self.states[3*_c : 3*_c+3] = Infty
            self.Mtg += self.m / self.a
            NewLogMtg = max(int(math.log(self.Mtg / self.m, self.q)), 0)
            if NewLogMtg != self.LogMtg:
                for _c2 in range(self._m):
                    newtriple = tuple(self.states[3*_c2 : 3*_c2+3] - NewLogMtg)
                    if newtriple not in self.Codebook and self.DeadFlags[3*_c2] == 1:
                        self.states[3*_c2 : 3*_c2+3] += NewLogMtg - self.LogMtg
                        cList += [3*_c2, 3*_c2+1, 3*_c2+2]
                self.LogMtg = NewLogMtg
            self.a = np.dot(np.power(self.q, -self.states), self.DeadFlags)
            self.snapshot = np.array([t, c, k, self.Mtg, self.a, self.LogMtg, self.DeadNum])
            return True, cList
        else:
            return False, []


class AdaThrsSketch(Sketch):
    # when the sum of sketches over the minimum value exceeds a half, raise the min value
    def __init__(self, pm, pq, pN, pUpbd, pcolor='yellow', pname="AdaThrs", pAdaFrac=0.5):
        super(AdaThrsSketch, self).__init__(pm, pq, pN, pcolor, pname, 8, 3*MaxChange)
        self.upbd = pUpbd
        self.DeadFlags = np.zeros(pm, dtype=int) + 1 # 1 for alive, 0 for dead
        self.Min = 0
        self.DeadNum = 0
        self.Sum = 0
        self.AdaFrac = pAdaFrac
        self.snapshotColStr += ["Min", "DeadNum", "Sum"]

    def update(self, c, k, t):
        if k > self.states[c] and self.DeadFlags[c] == 1:
            cList = [c]
            if k - self.Min > self.upbd:
                # this counter dead
                self.DeadNum += 1
                self.DeadFlags[c] = 0
                self.states[c] = Infty
            else:
                self.states[c] = k
            self.Mtg += self.m / self.a
            self.Min = np.min(self.states)
            LiveNum = self.m - self.DeadNum
            self.Sum = np.dot(self.states, self.DeadFlags) - self.Min * LiveNum
            SumThres = self.upbd * LiveNum * self.AdaFrac
            if self.Sum >= SumThres:
                NewMin = self.Min + int((self.Sum - SumThres) / LiveNum)
                for c2 in range(self.m):
                    if self.states[c2] < NewMin and self.DeadFlags[c2] == 1:
                        self.states[c2] = NewMin
                        cList += [c2]
                self.Min = NewMin
            self.a = np.dot(np.power(self.q, -self.states), self.DeadFlags)
            self.snapshot = np.array([t, c, k, self.Mtg, self.a, self.Min, self.DeadNum, self.Sum])
            return True, cList
        else:
            return False, []


class Min2CdbkSketch(Sketch):
    # the min of logMtg would be 2
    def __init__(self, pm, pq, pN, pCodebook, pcolor="orange", pname="Min2Cdbk"):
        _m = int(pm/3)
        m = _m * 3
        super(Min2CdbkSketch, self).__init__(m, pq, pN, pcolor, pname, 7, 3*MaxChange)
        self.Codebook = pCodebook
        self.DeadFlags = np.zeros(pm, dtype=int) + 1
        self._m = _m
        self.DeadNum = 0
        self.LogMtg = 2
        self.snapshotColStr += ["LogMtg", "DeadNum"]

    def update(self, c, k, t):
        if k > self.states[c] and self.DeadFlags[c] == 1:
            _c = int(c/3)
            cList = [3*_c, 3*_c+1, 3*_c+2]
            self.states[c] = k
            triple = tuple(self.states[3*_c : 3*_c+3] - self.LogMtg)
            if triple not in self.Codebook:
                self.DeadFlags[3*_c:3*_c+3] = 0
                self.DeadNum += 3
                self.states[3*_c : 3*_c+3] = Infty
            self.Mtg += self.m / self.a
            NewLogMtg = max(int(math.log(self.Mtg / self.m, self.q)), 2)
            if NewLogMtg != self.LogMtg:
                for _c2 in range(self._m):
                    newtriple = tuple(self.states[3*_c2 : 3*_c2+3] - NewLogMtg)
                    if newtriple not in self.Codebook and self.DeadFlags[3*_c2] == 1:
                        self.states[3*_c2 : 3*_c2+3] += NewLogMtg - self.LogMtg
                        cList += [3*_c2, 3*_c2+1, 3*_c2+2]
                self.LogMtg = NewLogMtg
            self.a = np.dot(np.power(self.q, -self.states), self.DeadFlags)
            self.snapshot = np.array([t, c, k, self.Mtg, self.a, self.LogMtg, self.DeadNum])
            return True, cList
        else:
            return False, []


class ArtifCdbkSketch(Sketch):
    def __init__(self, pm, pq, pN, pArtifCodebook, pcolor="pink", pname="ArtifCdbk"):
        _m = int(pm/3)
        m = _m * 3
        super(ArtifCdbkSketch, self).__init__(m, pq, pN, pcolor, pname, 7, 6*MaxChange)
        self.ArtifCodebook = pArtifCodebook
        self.DeadFlags = np.zeros(pm, dtype=int) + 1
        self._m = _m
        self.DeadNum = 0
        self.LogMtg = 2
        self.snapshotColStr += ["LogMtg", "DeadNum"]

    def update(self, c, k, t):
        if k > self.states[c] and self.DeadFlags[c] == 1:
            _c = int(c/3)
            cList = [3*_c, 3*_c+1, 3*_c+2]
            self.states[c] = k
            triple = tuple(self.states[3*_c : 3*_c+3] - self.LogMtg)
            newtriple, _ = self.ArtifCodebook(triple)
            self.states[3*_c : 3*_c+3] = newtriple
            self.states[3*_c : 3*_c+3] += self.LogMtg
            self.Mtg += self.m / self.a
            NewLogMtg = max(int(math.log(self.Mtg / self.m, self.q)), 2)
            if NewLogMtg != self.LogMtg:
                for _c2 in range(self._m):
                    triple2 = tuple(self.states[3*_c2 : 3*_c2+3] - NewLogMtg)
                    newtriple2, changed = self.ArtifCodebook(triple2)
                    self.states[3*_c2 : 3*_c2+3] = newtriple2
                    self.states[3*_c2 : 3*_c2+3] += NewLogMtg
                    if changed:
                        cList += [3*_c2, 3*_c2+1, 3*_c2+2]
                self.LogMtg = NewLogMtg
            self.a = np.dot(np.power(self.q, -self.states), self.DeadFlags)
            self.DeadNum = np.sum(np.where(self.states == Infty + self.LogMtg, 1, 0))
            self.snapshot = np.array([t, c, k, self.Mtg, self.a, self.LogMtg, self.DeadNum])
            return True, cList
        else:
            return False, []


def getTimeString():
    return time.strftime(time.strftime("%m_%d_%H_%M_%S"))


def unpack(pN, df, datname, inxmax):
    dat = np.zeros(pN)
    for inx in range(inxmax):
        d = df[datname][inx]
        mint = int(df["t"][inx])
        maxt = int(df["t"][inx+1]) if (inx < inxmax-1) else pN
        for pt in range(mint, maxt):
            dat[pt] = d
    return dat


def myplot(mSketches, datname, pN, pr, mtitle="", reference=True):
    x = np.arange(pN)
    if reference:
        plt.plot(x, x, color="black")
    for sketch in mSketches:
        datHist = unpack(N, sketch.snapshotHistdf, datname, sketch.snapshotHist_inx)
        plt.plot(x, datHist, color=sketch.color)
    plt.title(mtitle)
    plt.savefig("figs/"+VersionStr+"_"+datname+"_"+getTimeString()+"_("+str(pr) + ").png")
    plt.show()


def getCodebook(pSize):
    cdbkfile = 'codebooks/Codebook-' + str(Size) + '.pkl'
    with open(cdbkfile, "rb") as file:
        gCodebook = pickle.load(file)
    return gCodebook


def ArtifCodebook688(ptriple):
    # 689 states, one of them is inf, inf, inf, excluded when counting sizes
    # literally no death
    newtripl = [0, 0, 0]
    InfN = 0
    InfRang = [8, 8, 13]
    for l in range(3):
        if ptriple[l] <= -2:
            newtripl[l] = -2
        elif -1<=ptriple[l]<=2 and InfN == 0:
            newtripl[l] = ptriple[l]
        elif 3<=ptriple[l]<=4 and InfN == 0:
            newtripl[l] = 4
        elif 5<=ptriple[l]<=7 and InfN == 0:
            newtripl[l] = 7
        elif InfN != 0 and ptriple[l] < InfRang[InfN]:
            newtripl[l] = ptriple[l]
        elif ptriple[l] >= InfRang[InfN]:
            newtripl[l] = Infty
            InfN += 1
    changed = newtripl[0] == ptriple[0] and newtripl[1] == ptriple[1] and newtripl[2] == ptriple[2]
    return tuple(newtripl), changed


def ArtifCodebook631(ptriple):
    # 632 states, one of them is inf, inf, inf, excluded when counting sizes
    newtripl = [0, 0, 0]
    InfN = 0
    InfRang = [7, 7, 13]
    for l in range(3):
        if ptriple[l] <= -2:
            newtripl[l] = -2
        elif -1<=ptriple[l]<=2 and InfN == 0:
            newtripl[l] = ptriple[l]
        elif 3<=ptriple[l]<=4 and InfN == 0:
            newtripl[l] = 4
        elif 5<=ptriple[l]<=6 and InfN == 0:
            newtripl[l] = 6
        elif InfN != 0 and ptriple[l] < InfRang[InfN]:
            newtripl[l] = ptriple[l]
        elif ptriple[l] >= InfRang[InfN]:
            newtripl[l] = Infty
            InfN += 1
    changed = newtripl[0] == ptriple[0] and newtripl[1] == ptriple[1] and newtripl[2] == ptriple[2]
    return tuple(newtripl), changed


def ArtifCodebook568(ptriple):
    # 569 states, one of them is inf, inf, inf, excluded when counting sizes
    newtripl = [0, 0, 0]
    infN = 0
    CoDict0 = {-1:-1, 0:0, 1:1, 2:2, 3:3, 4:5, 5:5}
    CoDict1 = {-1:-1, 0:0, 1:1, 2:2, 3:3, 4:4, 5:6, 6:6}
    CoDict2 = {-1:-1, 0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8}
    for l in range(3):
        if ptriple[l] <= -2:
            newtripl[l] = -2
        elif -1<=ptriple[l]<=5:
            newtripl[l] = CoDict0[ptriple[l]]
        else:
            newtripl[l] = Infty
            infN += 1

    if infN == 1:
        for l in range(3):
            if ptriple[l] <= -2:
                newtripl[l] = -2
            elif -1 <= ptriple[l] <= 6:
                newtripl[l] = CoDict1[ptriple[l]]
            else:
                newtripl[l] = Infty
    elif infN == 2:
        for l in range(3):
            if ptriple[l] <= -2:
                newtripl[l] = -2
            elif -1 <= ptriple[l] <= 8:
                newtripl[l] = CoDict2[ptriple[l]]
            else:
                newtripl[l] = Infty

    changed = newtripl[0] == ptriple[0] and newtripl[1] == ptriple[1] and newtripl[2] == ptriple[2]
    return tuple(newtripl), changed


def ArtifCodebook393(ptriple):
    # 394 states, one of them is inf, inf, inf, excluded when counting sizes
    # (-2, -1, 0, 1, 2, 4)
    # 6*6*6 + 3*7*7+3*9+1
    newtripl = [0, 0, 0]
    infN = 0
    CoDict0 = {-1:-1, 0:0, 1:1, 2:2, 3:4, 4:4}
    CoDict1 = {-1:-1, 0:0, 1:1, 2:2, 3:4, 4:4, 5:6, 6:6}
    CoDict2 = {-1:-1, 0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7}
    for l in range(3):
        if ptriple[l] <= -2:
            newtripl[l] = -2
        elif -1<=ptriple[l]<=4:
            newtripl[l] = CoDict0[ptriple[l]]
        else:
            newtripl[l] = Infty
            infN += 1

    if infN == 1:
        for l in range(3):
            if ptriple[l] <= -2:
                newtripl[l] = -2
            elif -1 <= ptriple[l] <= 6:
                newtripl[l] = CoDict1[ptriple[l]]
            else:
                newtripl[l] = Infty
    elif infN == 2:
        for l in range(3):
            if ptriple[l] <= -2:
                newtripl[l] = -2
            elif -1 <= ptriple[l] <= 7:
                newtripl[l] = CoDict2[ptriple[l]]
            else:
                newtripl[l] = Infty

    changed = newtripl[0] == ptriple[0] and newtripl[1] == ptriple[1] and newtripl[2] == ptriple[2]
    return tuple(newtripl), changed


m = 300
q = 2.0
N = 100000
Upbd = 5
Round = 5
Size = 393
AdaFrac = 0.2
Codebook = getCodebook(Size)
title = "m=%d, q=%d, N=%d, Upbd=%d, CdbkSize=%d, AdaFrac=%.2f, Round=%d" % \
        (m, q, N, Upbd, Size, AdaFrac, Round)

for r in tqdm.tqdm(range(Round)):
    aLLSketch = LLSketch(m, q, N)
    aThrsSketch = ThrsSketch(m, q, N, Upbd)
    aAdaThreSketch = AdaThrsSketch(m, q, N, Upbd, pAdaFrac=AdaFrac)
    aCdbkSketch = CdbkSketch(m, q, N, Codebook)
    aMin2CdbkSketch = Min2CdbkSketch(m, q, N, Codebook)
    aArtifCdbkSketch = ArtifCdbkSketch(m, q, N, pcolor="purple", pArtifCodebook=ArtifCodebook393)
    Sketches = [aLLSketch, aCdbkSketch, aMin2CdbkSketch, aArtifCdbkSketch, aThrsSketch, aAdaThreSketch]
    DeathSketches = [aCdbkSketch, aMin2CdbkSketch, aArtifCdbkSketch, aThrsSketch, aAdaThreSketch]
    for t in range(N):
        c = np.random.randint(m)
        k = np.random.geometric(1/q)
        for sketch in Sketches:
            Rec, CList = sketch.update(c, k, t)
            if Rec:
                sketch.record(CList, t)

    for sketch in Sketches:
        sketch.savehist()

    myplot(Sketches, "Mtg", N, r, title)
    myplot(DeathSketches, "DeadNum", N, r, title, False)
