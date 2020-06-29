import math
import pandas as pd
from utils import *
from _trash import artifCodebooks as ac

scalingfactor = 1000
scalingfactors = [1, 1000, 1e6, 1e9, 1e12, 1e15, 1e18, 1e21, 1e24, 1e27, 1e30]

class Sketch:
    def __init__(self, pm, pq, pN, pcolor, pname, psnapshotLenNew=0, prunMaxChange=MaxChange,
                 pSnapshotHistexpand:int=1):
        self.name = pname
        self.color = pcolor
        self.m = pm
        self.q = pq
        self.N = pN
        self.states = np.zeros(pm, dtype=np.int64)
        self.Mtg = np.float64(0)
        self.a = np.float64(pm)
        self.rega = np.float64(1)
        self.invrega = np.float64(1)
        self.mtgScalinglvl = 0
        self.t = np.float64(0)

        self.runningHist = np.zeros((pm, 2*prunMaxChange), dtype=np.float64)
        self.runningColStr = ["time"+str(int(i/2)) if i%2==0 else "value"+str(int(i/2)) for i in range(2*prunMaxChange)]
        self.runningHist_inx = np.zeros(pm, dtype=int)
        self.runningHistdf = pd.DataFrame()

        self.snapshotLen = psnapshotLenNew + 7
        self.snapshotColStr = ["t", "c", "k", "Mtg", "a", "regA", "invRegA"]
        self.snapshot = np.zeros(self.snapshotLen, dtype=np.float64)
        self.snapshotHist = np.zeros((10000*pSnapshotHistexpand, self.snapshotLen))
        self.snapshotHist_inx: int = 0
        self.snapshotHistdf = pd.DataFrame()

    def update(self, c, k, t):
        return True, []

    def updateMtg(self):
        self.Mtg += self.m/self.a
        return
        # if self.Mtg > scalingfactor:
        #     self.Mtg /= scalingfactor
        #     self.mtgScalinglvl += 1
        # self.Mtg += deltaMtg/scalingfactors[self.mtgScalinglvl]
        # self.floatLogMtg = math.log(self.Mtg)+self.mtgScalinglvl*math.log(scalingfactor)

    def updateA(self, newA):
        self.a = newA
        self.rega = newA / self.m
        self.invrega = 1 / self.rega

    def updateSnapshot(self, t, c, k, newsnapshot):
            self.snapshot = np.hstack((
                np.array([t, c, k, self.Mtg, self.a, self.rega, self.invrega]),
                newsnapshot))
            self.t = t

    def record(self, cList, tosaveRunHist=True):
        if tosaveRunHist:
            for c in cList:
                self.runningHist[c][self.runningHist_inx[c]:self.runningHist_inx[c]+2] = (self.t, self.states[c])
                self.runningHist_inx[c] += 2
        self.snapshotHist[self.snapshotHist_inx] = self.snapshot
        self.snapshotHist_inx += 1

    def savehist(self, mode="excel", sr=0, tosaveRunHist=True):
        # 0 for both, 1 for only the snapshot, 2 for none of them.
        max_run_inx = np.max(self.runningHist_inx)+10
        if tosaveRunHist:
            self.runningHistdf = pd.DataFrame(self.runningHist[:, :2*max_run_inx], columns=self.runningColStr[:2*max_run_inx])
        self.snapshotHistdf = pd.DataFrame(self.snapshotHist[0:self.snapshotHist_inx, :], columns=self.snapshotColStr)
        if mode == "excel":
            sWriter = pd.ExcelWriter("TTLHist/"+VersionStr+"/"+self.name+"_"+getTimeString()+".xlsx")
            self.runningHistdf.to_excel(sWriter, "running")
            self.snapshotHistdf.to_excel(sWriter, "snapshot")
            sWriter.save()
        elif mode == "csv":
            self.runningHistdf.to_csv("TTLHist/"+VersionStr+"/"+self.name+"_running_"+getTimeString()+".csv")
            self.snapshotHistdf.to_csv("TTLHist/"+VersionStr+"/"+self.name+"_snapshots_"+getTimeString()+".csv")
        elif mode == "short":
            self.snapshotHistdf[["t", "Mtg", "invRegA"]].to_csv("TTLHist/"+VersionStr+"/"+RunStr+"_"
                                                                +"shortHist_"+self.name+"("+str(sr)+").csv")
        elif mode == "extracted":
            pass

    def refresh(self):
        self.states = np.zeros(self.m, dtype=np.int64)
        self.Mtg = np.float64(0)
        self.a = np.float64(self.m)
        self.rega = np.float64(1)
        self.invrega = np.float64(1)
        self.t = np.float64(0)
        self.mtgScalinglvl = 0
        self.runningHist_inx = np.zeros(self.runningHist_inx.shape, dtype=np.int)
        self.runningHist = np.zeros(self.runningHist.shape, dtype=np.float64)
        self.snapshotHist_inx = 0
        self.snapshotHist = np.zeros(self.snapshotHist.shape, dtype=np.float64)


class LLSketch(Sketch):
    def __init__(self, pm, pq, pN, pcolor="red", pname="LL"):
        super(LLSketch, self).__init__(pm, pq, pN, pcolor, pname)

    def update(self, c, k, t):
        if k > self.states[c]:
            self.updateMtg()
            self.updateA(self.a + np.power(self.q, -k) - np.power(self.q, -self.states[c]))
            self.states[c] = k
            self.updateSnapshot(t, c, k, [])
            return True, [c]
        else:
            return False, []


class ThrsSketch(Sketch):
    def __init__(self, pm, pq, pN, pUpbd, pcolor='green', pname="Thrs"):
        mpname = pname+"-"+str(pq)+"-"+str(pUpbd)
        super(ThrsSketch, self).__init__(pm, pq, pN, pcolor, mpname, 2)
        self.upbd = pUpbd
        self.DeadFlags = np.zeros(pm, dtype=int) + 1 # 1 for alive, 0 for dead
        self.Min = 0
        self.DeadNum = 0
        self.snapshotColStr += ["Min", "DeadNum"]

    def update(self, c, k, t):
        if k > self.states[c] and self.DeadFlags[c] == 1:
            if k - self.Min > self.upbd and self.DeadNum < self.m - 1:
                # this counter dead
                self.DeadNum += 1
                self.DeadFlags[c] = 0
                self.states[c] = Infty
            else:
                self.states[c] = k
            self.updateMtg()
            self.updateA(np.dot(np.power(self.q, -self.states), self.DeadFlags))
            self.Min = np.min(self.states)
            self.updateSnapshot(t, c, k, [self.Min, self.DeadNum])
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
        super(CdbkSketch, self).__init__(m, pq, pN, pcolor, mpname, 2, MaxChange)
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
            self.updateMtg()
            NewLogMtg = max(int(math.log(self.Mtg / self.m, self.q)+self.mtgScalinglvl*math.log(scalingfactor, self.q)), 0)
            if NewLogMtg != self.LogMtg:
                for _c2 in range(self._m):
                    newtriple = tuple(self.states[3*_c2 : 3*_c2+3] - NewLogMtg)
                    if newtriple not in self.Codebook and self.DeadFlags[3*_c2] == 1:
                        self.states[3*_c2 : 3*_c2+3] += NewLogMtg - self.LogMtg
                        cList += [3*_c2, 3*_c2+1, 3*_c2+2]
                self.LogMtg = NewLogMtg
            self.updateA(np.dot(np.power(self.q, -self.states), self.DeadFlags))
            self.updateSnapshot(t, c, k, [self.LogMtg, self.DeadNum])
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
        super(AdaThrsSketch, self).__init__(pm, pq, pN, pcolor, mpname, 3, MaxChange)
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
            self.updateMtg()
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
            self.updateA(np.dot(np.power(self.q, -self.states), self.DeadFlags))
            self.updateSnapshot(t, c, k, [self.Min, self.DeadNum, self.Sum])
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
        super(Min2CdbkSketch, self).__init__(m, pq, pN, pcolor, mpname, 2, MaxChange)
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
            self.updateMtg()
            NewLogMtg = max(int(math.log(self.Mtg / self.m, self.q)+self.mtgScalinglvl*math.log(scalingfactor, self.q)), 2)
            if NewLogMtg != self.LogMtg:
                for _c2 in range(self._m):
                    newtriple = tuple(self.states[3*_c2 : 3*_c2+3] - NewLogMtg)
                    if newtriple not in self.Codebook and self.DeadFlags[3*_c2] == 1:
                        self.states[3*_c2 : 3*_c2+3] += NewLogMtg - self.LogMtg
                        cList += [3*_c2, 3*_c2+1, 3*_c2+2]
                self.LogMtg = NewLogMtg
            self.updateA(np.dot(np.power(self.q, -self.states), self.DeadFlags))
            self.updateSnapshot(t, c, k, [self.LogMtg, self.DeadNum])
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
        super(ArtifCdbkSketch, self).__init__(m, pq, pN, pcolor, mpname, 2, MaxChange)
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
            self.updateMtg()
            NewLogMtg = max(int(math.log(self.Mtg / self.m, self.q)+self.mtgScalinglvl*math.log(scalingfactor, self.q)), 2)
            if NewLogMtg != self.LogMtg:
                for _c2 in range(self._m):
                    triple2 = tuple(self.states[3*_c2 : 3*_c2+3] - NewLogMtg)
                    newtriple2, changed = self.ArtifCodebook(triple2)
                    self.states[3*_c2 : 3*_c2+3] = newtriple2
                    self.states[3*_c2 : 3*_c2+3] += NewLogMtg
                    if changed:
                        cList += [3*_c2, 3*_c2+1, 3*_c2+2]
                self.LogMtg = NewLogMtg
            self.updateA(np.sum(np.power(self.q, -self.states)))
            self.DeadNum = np.sum(np.where(self.states == Infty + self.LogMtg, 1, 0))
            self.updateSnapshot(t, c, k, [self.LogMtg, self.DeadNum])
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
        super(ArtifCdbkNSketch, self).__init__(m, pq, pN, pcolor, mpname, 2, MaxChange)
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
            self.updateMtg()
            NewLogMtg = max(int(math.log(self.Mtg / self.m, self.q)+math.log(scalingfactor, self.q)*self.mtgScalinglvl), 2)
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
            self.updateA(np.sum(np.power(self.q, -self.states)))
            self.DeadNum = np.sum(np.where(self.states == Infty + self.LogMtg, 1, 0))
            self.updateSnapshot(t, c, k, [self.LogMtg, self.DeadNum])
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
            self.updateMtg()
            # this part is very ad hoc: I exploited the fact that in our simulation self.diffbd would be 4
            self.states[c] = k
            for i in range(1, 11):
                if c - i >= 0 and self.states[c-i] < k-i*self.diffbd:
                    self.states[c-i] = k-i*self.diffbd
                    cList.append(c-i)
                if c + i < self.m and self.states[c+i] < k-i*self.diffbd:
                    self.states[c+i] = k-i*self.diffbd
                    cList.append(c+i)
            self.updateA(np.sum(np.power(self.q, -self.states)))
            self.updateSnapshot(t, c, k, [])
            return True, cList
        else:
            return False, []

    # you do not need to redefine refresh function for Curtain sketch!


class CurtainSawTeethSketch(Sketch):
    # this sketch ensures the difference of adjacent counters <= pDiffbd.
    def __init__(self, pm, pq, pN, pDiffbd, pcolor='orange', pname="CtnSawTeeth"):
        mpname = pname+"-"+str(pq)+"-"+str(pDiffbd)
        super(CurtainSawTeethSketch, self).__init__(pm, pq, pN, pcolor, mpname)
        self.diffbd = pDiffbd # ad hoc: this value would be 3.5
        ceofx = np.arange(pm)
        self.offset = np.where(ceofx%2==0, 0.5, 0)
        self.a = np.sum(np.power(self.q, -self.states - self.offset))

    def update(self, c, k, t):
        if k > self.states[c]:
            cList = [c]
            self.updateMtg()
            # this part is very ad hoc: I exploited the fact that in our simulation self.diffbd would be 3.5
            self.states[c] = k
            for i in range(1, 11):
                if c - i >= 0 and self.states[c-i] + self.offset[c-i] < k + self.offset[c] - i * self.diffbd:
                    self.states[c-i] = k-i*self.diffbd + self.offset[c] - self.offset[c-i]
                    cList.append(c-i)
                if c + i < self.m and self.states[c+i] + self.offset[c+i] < k + self.offset[c] - i * self.diffbd:
                    self.states[c+i] = k-i*self.diffbd
                    cList.append(c+i)
            self.updateA(np.sum(np.power(self.q, -self.states-self.offset)))
            self.updateSnapshot(t, c, k, [])
            return True, cList
        else:
            return False, []


class CurtainSTUnifOffstSketch(Sketch):
    # this sketch ensures the difference of adjacent counters <= pDiffbd.
    def __init__(self, pm, pq, pN, pDiffbd, pcolor='orange', pname="CtnSTUnifOffs"):
        mpname = pname+"-"+str(pq)+"-"+str(pDiffbd)
        super(CurtainSTUnifOffstSketch, self).__init__(pm, pq, pN, pcolor, mpname)
        self.diffbd = pDiffbd # ad hoc: this value would be 4
        ceofx = np.arange(pm)
        self.sawtoffset = np.where(ceofx%2==0, 0.5, 0)
        self.offset = np.where(ceofx%2==0, 0.5, 0) + np.array(np.arange(pm), dtype=np.float)/(2*pm)
        self.a = np.sum(np.power(self.q, -self.states - self.offset))

    def update(self, c, k, t):
        if k > self.states[c]:
            cList = [c]
            self.updateMtg()
            # this part is very ad hoc: I exploited the fact that in our simulation self.diffbd would be 3.5
            self.states[c] = k
            for i in range(1, 11):
                if c - i >= 0 and (self.states[c]+self.sawtoffset[c]-self.states[c-i]-self.sawtoffset[c-i] > self.diffbd*i):
                    self.states[c-i] = k-i*self.diffbd + self.sawtoffset[c] - self.sawtoffset[c-i]
                    cList.append(c-i)
                if c + i < self.m and self.states[c+i] + self.sawtoffset[c+i] < k + self.sawtoffset[c] - i * self.diffbd:
                    self.states[c+i] = k-i*self.diffbd + self.sawtoffset[c] - self.sawtoffset[c-i]
                    cList.append(c+i)
            self.updateA(np.sum(np.power(self.q, -self.states-self.offset)))
            self.updateSnapshot(t, c, k, [])
            return True, cList
        else:
            return False, []


class CurtainPCSASketch(Sketch):
    # this sketch ensures the difference of adjacent counters <= pDiffbd.
    # this sketch has not finished.
    def __init__(self, pm, pq, pN, pDiffbd, bitmapRange, pcolor='orange', pname="CtnPCSA"):
        mpname = pname + "-" + str(pq) + "-" + str(pDiffbd)
        super(CurtainPCSASketch, self).__init__(pm, pq, pN, pcolor, mpname)
        self.bitmap = np.ones((pm, bitmapRange)) # the first bit would always be 1, so not stored in this bitmap
        # in the beginning all states[c] = 1 so we should let the bitmap all be 1
        self.bitmapRange = bitmapRange
        self.diffbd = pDiffbd # ad hoc: this value would be 3.5
        ceofx = np.arange(pm)
        self.sawtoffset = np.where(ceofx%2==0, 0.5, 0)
        self.offset = np.where(ceofx%2==0, 0.5, 0) + np.array(np.arange(pm), dtype=np.float64)/(2*pm)
        self.a = np.sum(np.power(self.q, -self.states - self.offset))

    def update(self, c, k, t):
        if k > self.states[c] or self.states[c]-self.bitmapRange <= k < self.states[c]:
            oldstate = self.states[c]
            if k < self.states[c]:
                if self.bitmap[c, oldstate - k - 1] == 0:
                    self.updateMtg()
                    self.bitmap[c, oldstate - k - 1] = 1
                    probBitmap = np.vstack(tuple((1 + np.arange(self.bitmapRange)- self.states[i] - self.offset[i]) for i in range(self.m)))
                    remainingAreaBitmap = np.sum(np.multiply(1-self.bitmap, np.power(self.q, probBitmap)))*(1-1/self.q)
                    self.updateA(remainingAreaBitmap + np.sum(np.power(self.q, -self.states-self.offset)))
                    self.updateSnapshot(t, c, k, [])
                    return True, [c]
                else:
                    return False, []
            else:
                self.states[c] = k
                cList = [c]
                self.updateMtg()
                newkbitmap = np.zeros(self.bitmapRange)
                for j in range(self.bitmapRange):
                    if k - 1 - j == oldstate:
                        newkbitmap[j] = 1
                    elif k - 1 - j < oldstate:
                        if k - 1 - j >= 0:
                            newkbitmap[j] = self.bitmap[c, oldstate-k+j]
                        else:
                            newkbitmap[j] = 1
                self.bitmap[c] = newkbitmap
                for i in range(11):
                    if c - i >= 0 and self.states[c-i] + self.offset[c-i] < k + self.offset[c] - i * self.diffbd:
                        oldCMIstate = self.states[c-i]
                        self.states[c-i] = k-i*self.diffbd + self.offset[c] - self.offset[c-i]
                        newCMIstate = self.states[c-i]
                        cList.append(c-i)
                        newCMIbitmap = np.zeros(self.bitmapRange)
                        for j in range(self.bitmapRange):
                            if newCMIstate - 1 - j == oldCMIstate:
                                newCMIbitmap[j] = 1
                            elif newCMIstate - 1 - j <= oldCMIstate - 1:
                                if newCMIstate - 1 - j >= 0:
                                    newCMIbitmap[j] = self.bitmap[c-i, oldCMIstate - newCMIstate + j]
                                else:
                                    newCMIbitmap[j] = 1
                        self.bitmap[c-i] = newCMIbitmap
                    if c + i < self.m and self.states[c+i] + self.offset[c+i] < k + self.offset[c] - i * self.diffbd:
                        oldCPIstate = self.states[c+i]
                        self.states[c+i] = k-i*self.diffbd + self.offset[c] - self.offset[c-i]
                        newCPIstate = self.states[c+i]
                        cList.append(c+i)
                        newCPIbitmap = np.zeros(self.bitmapRange)
                        for j in range(self.bitmapRange):
                            if newCPIstate - 1 - j == oldCPIstate:
                                newCPIbitmap[j] = 1
                            elif newCPIstate - 1 - j <= oldCPIstate - 1:
                                if newCPIstate - 1 - j >= 0:
                                    newCPIbitmap[j] = self.bitmap[c+i, oldCPIstate - newCPIstate + j]
                                else:
                                    newCPIbitmap[j] = 1
                        self.bitmap[c+i] = newCPIbitmap
                probBitmap = np.vstack(tuple((1 + np.arange(self.bitmapRange)- self.states[i] - self.offset[i]) for i in range(self.m)))
                remainingAreaBitmap = np.sum(np.multiply(1 - self.bitmap, np.power(self.q, probBitmap))) * (1 - 1/self.q)
                self.updateA(remainingAreaBitmap + np.sum(np.power(self.q, -self.states - self.offset)))
                self.updateSnapshot(t, c, k, [])
                return True, cList
        else:
            return False, []


class CurtainStarSketch(Sketch):
    def __init__(self, pm, pq, pN, pUpbd, pcolor='green', pname="CtnStar"):
        mpname = pname+"-"+str(pq)+"-"+str(pUpbd)
        super(CurtainStarSketch, self).__init__(pm, pq, pN, pcolor, mpname, 1)
        self.upbd = pUpbd
        self.Min = 0
        self.snapshotColStr += ["Min"]

    def update(self, c, k, t):
        if k > self.states[c]:
            self.states[c] = k
            cList = [c]
            if k - self.Min > self.upbd:
                self.Min = k - self.upbd
            for i in range(self.m):
                if self.states[i] < self.Min:
                    self.states[i] = self.Min
                    cList.append(i)
            self.updateMtg()
            self.updateA(np.sum(np.power(self.q, -self.states)))
            self.updateSnapshot(t, c, k, [self.Min])
            return True, cList
        else:
            return False, []

    def refresh(self):
        super(CurtainStarSketch, self).refresh()
        self.Min = 0


def updategen(usketch:Sketch):
    if type(usketch) == CurtainPCSASketch:
        assert hasattr(usketch, "offset")
        assert hasattr(usketch, "bitmapRange")
        assert hasattr(usketch, "bitmap")
        remainingArea = np.float64(usketch.a/usketch.m)
        if remainingArea < 1e-8:
            deltat = np.float64(np.random.exponential(1/remainingArea))
        else:
            deltat = np.float64(np.random.geometric(remainingArea))
        probBitmap = np.vstack(tuple((1 + np.arange(usketch.bitmapRange)-usketch.states[i]-usketch.offset[i]) for i in range(usketch.m)))
        remainingAreaBitmap = np.sum(np.multiply(1 - usketch.bitmap, np.power(usketch.q, probBitmap)), axis=1) * (1 - 1/usketch.q)
        probList = np.power(1/usketch.q, usketch.states + usketch.offset) + remainingAreaBitmap
        probListsum = np.sum(probList)
        c = np.random.choice(np.arange(usketch.m), p=probList/probListsum)
        probList_ = np.array([np.power(1/usketch.q, usketch.states[c]+usketch.offset[c]), remainingAreaBitmap[c]])
        k_ = np.random.choice([0, 1], p=probList_/(np.sum(probList_)))
        if k_ == 0:
            k = usketch.states[c] + np.random.geometric(1-1/usketch.q)
        else:
            bitmapProblist = np.multiply(1-usketch.bitmap[c], np.power(usketch.q, np.arange(usketch.bitmapRange)))
            k0 = np.random.choice(np.arange(usketch.bitmapRange), p=bitmapProblist/(np.sum(bitmapProblist)))
            k = usketch.states[c] - 1 - k0
        return np.float64(usketch.t+deltat), c, k
    remainingArea = np.float64(usketch.a / usketch.m)
    if remainingArea < 1e-8:
        deltat = np.float64(np.random.exponential(1/remainingArea))
    else:
        deltat = np.float64(np.random.geometric(remainingArea))
    if hasattr(usketch, "offset"):
        prob = np.power(1/usketch.q, usketch.states + usketch.offset)
    else:
        prob = np.power(1/usketch.q, usketch.states)
    condprob = prob / np.sum(prob)
    c = np.random.choice(np.arange(usketch.m), p=condprob)
    # prob of at least k
    # = sum_k^infty (1-(1-1/q))^(i-1)(1-1/q)
    # = (1/q)^{k-1}-(1/q)^{k} + ...
    # = (1/q)^(k-1) :
    # now you are at k, so the prob of at least k+1 is 1/q^k
    k = usketch.states[c] + np.random.geometric(1-1/usketch.q)
    newt = np.float64(usketch.t+deltat)
    return newt, c, k

