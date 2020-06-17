import numpy as np
import math
import pandas as pd
from utils import *
import artifCodebooks as ac


class Sketch:
    def __init__(self, pm, pq, pN, pcolor, pname, psnapshotLen=5, prunMaxChange=MaxChange,
                 pSnapshotHistexpand:int=1):
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
        self.snapshotHist = np.zeros((MaxChange*pm*pSnapshotHistexpand, self.snapshotLen))
        self.snapshotHist_inx: int = 0
        self.snapshotHistdf = pd.DataFrame()

    def update(self, c, k, t):
        # if updated, return True; not updated, return False
        # remember to update the snapshot
        # and return a list of coords to updated
        return True, []

    def record(self, cList, t):
        for c in cList:
            runningHist_inx_c = int(self.runningHist_inx[c])
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

    def refresh(self):
        self.states = np.zeros(self.m, dtype=int)
        self.Mtg = 0
        self.a = self.m
        self.runningHist_inx = np.zeros(self.runningHist_inx.shape, dtype=int)
        self.runningHist = np.zeros(self.runningHist.shape)
        self.snapshotHist = np.zeros(self.snapshotHist.shape)
        self.snapshotHist_inx = 0


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
        mpname = pname+"-"+str(pUpbd)
        super(ThrsSketch, self).__init__(pm, pq, pN, pcolor, mpname, 7)
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

    def refresh(self):
        super(ThrsSketch, self).refresh()
        self.Min = 0
        self.DeadNum = 0
        self.DeadFlags = np.zeros(self.DeadFlags.shape) + 1


class CdbkSketch(Sketch):
    def __init__(self, pm, pq, pN, pCodebookSize, pcolor="blue", pname="Cdbk"):
        _m = int(pm/3)
        m = _m * 3
        mpname = pname+"-"+str(pCodebookSize)
        super(CdbkSketch, self).__init__(m, pq, pN, pcolor, mpname, 7, 3*MaxChange)
        self.Codebook = getCodebook(pCodebookSize)
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

    def refresh(self):
        super(CdbkSketch, self).refresh()
        self.DeadFlags = np.zeros(self.DeadFlags.shape) + 1
        self.DeadNum = 0
        self.LogMtg = 0


class AdaThrsSketch(Sketch):
    # when the sum of sketches over the minimum value exceeds a half, raise the min value
    def __init__(self, pm, pq, pN, pUpbd, pcolor='yellow', pname="AdaThrs", pAdaFrac=0.5):
        mpname = pname + "-" + str(pUpbd) + "-" + str(pAdaFrac)
        super(AdaThrsSketch, self).__init__(pm, pq, pN, pcolor, mpname, 8, 3*MaxChange)
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

    def refresh(self):
        super(AdaThrsSketch, self).refresh()
        self.DeadFlags = np.zeros(self.DeadFlags.shape) + 1
        self.Min = 0
        self.DeadNum = 0
        self.Sum = 0


class Min2CdbkSketch(Sketch):
    # the min of logMtg would be 2
    def __init__(self, pm, pq, pN, pCodebookSize, pcolor="orange", pname="Min2Cdbk"):
        _m = int(pm/3)
        m = _m * 3
        mpname = pname+"-"+str(pCodebookSize)
        super(Min2CdbkSketch, self).__init__(m, pq, pN, pcolor, mpname, 7, 3*MaxChange)
        self.Codebook = getCodebook(pCodebookSize)
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

    def refresh(self):
        super(Min2CdbkSketch, self).refresh()
        self.DeadFlags = np.zeros(self.DeadFlags.shape) + 1
        self.DeadNum = 0
        self.LogMtg = 2


class ArtifCdbkSketch(Sketch):
    def __init__(self, pm, pq, pN, pArtifCodebookName, pcolor="purple", pname="ArtifCdbk"):
        _m = int(pm/3)
        m = _m * 3
        mpname = pname+"-"+pArtifCodebookName
        super(ArtifCdbkSketch, self).__init__(m, pq, pN, pcolor, mpname, 7, 6*MaxChange)
        self.ArtifCodebook = getattr(ac, pArtifCodebookName)
        self._m = _m
        self.DeadNum = 0
        self.LogMtg = 2
        self.snapshotColStr += ["LogMtg", "DeadNum"]

    def update(self, c, k, t):
        if k > self.states[c]:
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
            self.a = np.sum(np.power(self.q, -self.states))
            self.DeadNum = np.sum(np.where(self.states == Infty + self.LogMtg, 1, 0))
            self.snapshot = np.array([t, c, k, self.Mtg, self.a, self.LogMtg, self.DeadNum])
            return True, cList
        else:
            return False, []

    def refresh(self):
        super(ArtifCdbkSketch, self).refresh()
        self.DeadNum = 0
        self.LogMtg = 2


class ArtifCdbkNSketch(Sketch):
    def __init__(self, pm, pq, pN, pArtifCodebookName, pcolor="purple", pname="ArtifCdbkN"):
        _m = int(pm/3)
        m = _m * 3
        mpname = pname+"-"+pArtifCodebookName
        super(ArtifCdbkNSketch, self).__init__(m, pq, pN, pcolor, mpname, 7, 6*MaxChange)
        self.ArtifCodebook = getattr(ac, pArtifCodebookName)
        self._m = _m
        self.DeadNum = 0
        self.LogMtg = 2
        pSize = getattr(ac, pArtifCodebookName+"Size")
        self.Codebook = getCodebook(pSize)
        self.snapshotColStr += ["LogMtg", "DeadNum"]

    def update(self, c, k, t):
        if k > self.states[c]:
            _c = int(c/3)
            cList = [3*_c, 3*_c+1, 3*_c+2]
            self.states[c] = k
            triple = tuple(self.states[3*_c : 3*_c+3] - self.LogMtg)
            if triple not in self.Codebook:
                newtriple, _ = self.ArtifCodebook(triple)
                self.states[3*_c : 3*_c+3] = newtriple
                self.states[3*_c : 3*_c+3] += self.LogMtg
            self.Mtg += self.m / self.a
            NewLogMtg = max(int(math.log(self.Mtg / self.m, self.q)), 2)
            if NewLogMtg != self.LogMtg:
                for _c2 in range(self._m):
                    triple2 = tuple(self.states[3*_c2 : 3*_c2+3] - NewLogMtg)
                    if triple2 not in self.Codebook:
                        newtriple2, changed = self.ArtifCodebook(triple2)
                        self.states[3*_c2 : 3*_c2+3] = newtriple2
                        self.states[3*_c2 : 3*_c2+3] += NewLogMtg
                        if changed:
                            cList += [3*_c2, 3*_c2+1, 3*_c2+2]
                self.LogMtg = NewLogMtg
            self.a = np.sum(np.power(self.q, -self.states))
            self.DeadNum = np.sum(np.where(self.states == Infty + self.LogMtg, 1, 0))
            self.snapshot = np.array([t, c, k, self.Mtg, self.a, self.LogMtg, self.DeadNum])
            return True, cList
        else:
            return False, []

    def refresh(self):
        super(ArtifCdbkNSketch, self).refresh()
        self.DeadNum = 0
        self.LogMtg = 2


class CurtainSketch(Sketch):
    # this sketch ensures the difference of adjacent counters <= pDiffbd.
    def __init__(self, pm, pq, pN, pDiffbd, pcolor='orange', pname="Crtn"):
        mpname = pname+"-"+str(pDiffbd)
        super(CurtainSketch, self).__init__(pm, pq, pN, pcolor, mpname)
        self.diffbd = pDiffbd

    def update(self, c, k, t):
        if k > self.states[c]:
            cList = [c]
            self.Mtg += self.m / self.a
            # this part is very ad hoc: I exploited the fact that in our simulation self.diffbd would be 4
            self.states[c] = k
            for i in [1, 2, 3, 4, 5]:
                if c - i >= 0 and self.states[c-i] < k-i*self.diffbd:
                    self.states[c-i] = k-i*self.diffbd
                    cList.append(c-i)
                if c + i < self.m and self.states[c+i] < k-i*self.diffbd:
                    self.states[c+i] = k-i*self.diffbd
                    cList.append(c+i)
            self.a = np.sum(np.power(self.q, -self.states))
            self.snapshot = np.array([t, c, k, self.Mtg, self.a])
            return True, cList
        else:
            return False, []

    # you do not need to redefine refresh function for Curtain sketch!


class CurtainEvenOffsetSketch(Sketch):
    # this sketch ensures the difference of adjacent counters <= pDiffbd.
    def __init__(self, pm, pq, pN, pDiffbd, pcolor='orange', pname="CtnEvnOfs"):
        mpname = pname+"-"+str(pDiffbd)
        super(CurtainEvenOffsetSketch, self).__init__(pm, pq, pN, pcolor, mpname)
        self.diffbd = pDiffbd # ad hoc: this value would be 3.5
        self.ofp = 1/math.sqrt(self.q)
        ceofx = np.arange(pm)
        self.offset = np.where(ceofx%2==0, 0.5, 0)

    def update(self, c, k, t):
        if c % 2 == 0:
            coin = np.random.rand()
            if coin > self.ofp:
                return False, []

        if k > self.states[c]:
            cList = [c]
            self.Mtg += self.m / self.a
            # this part is very ad hoc: I exploited the fact that in our simulation self.diffbd would be 3.5
            self.states[c] = k
            for i in [1, 2, 3, 4, 5]:
                if c - i >= 0 and self.states[c-i] + self.offset[c-i] < k + self.offset[c] - i * self.diffbd:
                    self.states[c-i] = k-i*self.diffbd + self.offset[c] - self.offset[c-i]
                    cList.append(c-i)
                if c + i < self.m and self.states[c+i] + self.offset[c+i] < k + self.offset[c] - i * self.diffbd:
                    self.states[c+i] = k-i*self.diffbd
                    cList.append(c+i)
            self.a = np.sum(np.power(self.q, -self.states-self.offset))
            self.snapshot = np.array([t, c, k, self.Mtg, self.a])
            return True, cList
        else:
            return False, []
