import math
import pandas as pd
from utils import *
from _trash import artifCodebooks as ac

scalingfactor = 1000
scalingfactors = [1, 1000, 1e6, 1e9, 1e12, 1e15, 1e18, 1e21, 1e24, 1e27, 1e30]
CurtainUpbd = 100
SnapMaxChange = 100000
PCSAUpbd = 40


class Sketch:
    def __init__(self, pm, pq, pN, pcolor, pname, psnapshotLenNew=0, prunhistLenNew=0, prunMaxChange=MaxChange):
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
        self.runningColSingStr = ["time", "value"]
        self.runningColSingStrLen = 2 + prunhistLenNew
        self.runningColStr = [colstr + str(i) for i in range(prunMaxChange) for colstr in self.runningColSingStr]
        self.runningHistNewcontent = np.zeros((self.m, prunhistLenNew), dtype=np.float64)
        self.runningHist_inx = np.zeros(pm, dtype=int)
        self.runningHistdf = pd.DataFrame()

        self.snapshotLen = psnapshotLenNew + 7
        self.snapshotColStr = ["t", "c", "k", "Mtg", "a", "regA", "invRegA"]
        self.snapshot = np.zeros(self.snapshotLen, dtype=np.float64)
        self.snapshotHist = np.zeros((SnapMaxChange, self.snapshotLen))
        self.snapshotHist_inx: int = 0
        self.snapshotHistdf = pd.DataFrame()

    def update(self, c, k, t):
        return True, []

    def updateMtg(self):
        self.Mtg += self.invrega
        return

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
                if self.runningColSingStrLen != 2:
                    self.runningHist[c][self.runningHist_inx[c]+2:self.runningHist_inx[c]+self.runningColSingStrLen] = self.runningHistNewcontent[c]
                self.runningHist_inx[c] += self.runningColSingStrLen
        self.snapshotHist[self.snapshotHist_inx] = self.snapshot
        self.snapshotHist_inx += 1

    def savehist(self, mode="excel", sr=0, tosaveRunHist=True):
        # 0 for both, 1 for only the snapshot, 2 for none of them.
        max_run_inx = int(np.max(self.runningHist_inx)/self.runningColSingStrLen)+1
        self.runningColStr = [colstr + str(i) for i in range(int(len(self.runningColStr)/self.runningColSingStrLen))
                              for colstr in self.runningColSingStr]
        if tosaveRunHist:
            self.runningHistdf = pd.DataFrame(self.runningHist[:, :self.runningColSingStrLen*max_run_inx],
                                              columns=self.runningColStr[:self.runningColSingStrLen*max_run_inx])
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
        self.runningHistNewcontent = np.zeros(self.runningHistNewcontent.shape)
        self.snapshotHist_inx = 0
        self.snapshotHist = np.zeros(self.snapshotHist.shape, dtype=np.float64)

    def updategen(self):
        remainingArea = np.float64(self.a / self.m)
        if remainingArea < 1e-8:
            deltat = np.float64(np.random.exponential(1 / remainingArea))
        else:
            deltat = np.float64(np.random.geometric(remainingArea))
        if hasattr(self, "offset"):
            prob = np.power(1 / self.q, self.states + self.offset)
        else:
            prob = np.power(1 / self.q, self.states)
        condprob = prob / np.sum(prob)
        c = np.random.choice(np.arange(self.m), p=condprob)
        # prob of at least k
        # = sum_k^infty (1-(1-1/q))^(i-1)(1-1/q)
        # = (1/q)^{k-1}-(1/q)^{k} + ...
        # = (1/q)^(k-1) :
        # now you are at k, so the prob of at least k+1 is 1/q^k
        k = self.states[c] + np.random.geometric(1 - 1 / self.q)
        newt = np.float64(self.t + deltat)
        return newt, c, k


class LLSketch(Sketch):
    def __init__(self, pm, pq, pN, pcolor="red", pname="LL"):
        mpname = "-".join([pname, str(pm), str(pq)])
        super(LLSketch, self).__init__(pm, pq, pN, pcolor, mpname)

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
        mpname = "-".join([pname, str(pm), str(pq), str(pUpbd)])
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
        mpname = "-".join([pname, str(pm), str(pq), str(pCodebookSize)])
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
        mpname = "-".join([pname, str(pm), str(pq), str(pUpbd), str(pAdaFrac)])
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
        mpname = "-".join([pname, str(pm), str(pq), str(pCodebookSize)])
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
        mpname = "-".join([pname, str(pm), str(pq), str(pArtifCodebookName)])
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
        mpname = "-".join([pname, str(pm), str(pq), str(pArtifCodebookName)])
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
    def __init__(self, pm, pq, pN, pDiffbd, pcolor='orange', pname="CrtnLL"):
        mpname = "-".join([pname, str(pm), str(pq), str(pDiffbd)])
        super(CurtainSketch, self).__init__(pm, pq, pN, pcolor, mpname)
        self.diffbd = pDiffbd

    def update(self, c, k, t):
        if k > self.states[c]:
            cList = [c]
            self.updateMtg()
            self.states[c] = k
            for i in range(1, CurtainUpbd):
                if c - i >= 0 and self.states[c-i] < k-i*self.diffbd:
                    self.states[c-i] = k-i*self.diffbd
                    cList.append(c-i)
                if c + i < self.m and self.states[c+i] < k-i*self.diffbd:
                    self.states[c+i] = k-i*self.diffbd
                    cList.append(c+i)
                if k-i*self.diffbd < 0:
                    break
            self.updateA(np.sum(np.power(self.q, -self.states)))
            self.updateSnapshot(t, c, k, [])
            return True, cList
        else:
            return False, []

    # you do not need to redefine refresh function for Curtain sketch!


class CurtainSawTeethSketch(Sketch):
    # this sketch ensures the difference of adjacent counters <= pDiffbd.
    def __init__(self, pm, pq, pN, pDiffbd, pcolor='orange', pname="CtnSawTeethLL"):
        mpname = "-".join([pname, str(pm), str(pq), str(pDiffbd)])
        super(CurtainSawTeethSketch, self).__init__(pm, pq, pN, pcolor, mpname)
        self.diffbd = pDiffbd
        ceofx = np.arange(pm)
        self.offset = np.where(ceofx%2==0, 0.5, 0)
        self.a = np.sum(np.power(self.q, -self.states - self.offset))

    def update(self, c, k, t):
        if k > self.states[c]:
            cList = [c]
            self.updateMtg()
            self.states[c] = k
            for i in range(1, CurtainUpbd):
                if c - i >= 0 and self.states[c-i] + self.offset[c-i] < k + self.offset[c] - i * self.diffbd:
                    self.states[c-i] = k-i*self.diffbd + self.offset[c] - self.offset[c-i]
                    cList.append(c-i)
                if c + i < self.m and self.states[c+i] + self.offset[c+i] < k + self.offset[c] - i * self.diffbd:
                    self.states[c+i] = k-i*self.diffbd
                    cList.append(c+i)
                if k-i*self.diffbd < 0:
                    break
            self.updateA(np.sum(np.power(self.q, -self.states-self.offset)))
            self.updateSnapshot(t, c, k, [])
            return True, cList
        else:
            return False, []


class CurtainSTUnifOffstSketch(Sketch):
    # this sketch ensures the difference of adjacent counters <= pDiffbd.
    def __init__(self, pm, pq, pN, pDiffbd, pcolor='orange', pname="CtnSTUnifOffsLL"):
        mpname = "-".join([pname, str(pm), str(pq), str(pDiffbd)])
        super(CurtainSTUnifOffstSketch, self).__init__(pm, pq, pN, pcolor, mpname)
        self.diffbd = pDiffbd
        ceofx = np.arange(pm)
        self.sawtoffset = np.where(ceofx%2==0, 0.5, 0)
        self.offset = np.where(ceofx%2==0, 0.5, 0) + np.array(np.arange(pm), dtype=np.float64)/(2*pm)
        self.a = np.sum(np.power(self.q, -self.states - self.offset))

    def refresh(self):
        super(CurtainSTUnifOffstSketch, self).refresh()
        self.updateA(np.sum(np.power(self.q, -self.states - self.offset)))

    def update(self, c, k, t):
        if k > self.states[c]:
            cList = [c]
            self.updateMtg()
            self.states[c] = k
            for i in range(1, CurtainUpbd):
                if c - i >= 0 and (self.states[c]+self.sawtoffset[c]-self.states[c-i]-self.sawtoffset[c-i] > self.diffbd*i):
                    self.states[c-i] = k-i*self.diffbd + self.sawtoffset[c] - self.sawtoffset[c-i]
                    cList.append(c-i)
                if c + i < self.m and self.states[c+i] + self.sawtoffset[c+i] < k + self.sawtoffset[c] - i * self.diffbd:
                    self.states[c+i] = k-i*self.diffbd + self.sawtoffset[c] - self.sawtoffset[c-i]
                    cList.append(c+i)
                if k-i*self.diffbd < 0:
                    break
            self.updateA(np.sum(np.power(self.q, -self.states-self.offset)))
            self.updateSnapshot(t, c, k, [])
            return True, cList
        else:
            return False, []


class CurtainPCSASketch(Sketch):
    def __init__(self, pm, pq, pN, pDiffbd, bitmapRange, pcolor='orange', pname="CtnPCSA"):
        mpname = "-".join([pname, str(pm), str(pq), str(pDiffbd), str(bitmapRange)])
        super(CurtainPCSASketch, self).__init__(pm, pq, pN, pcolor, mpname ,prunhistLenNew=bitmapRange)
        self.bitmap = np.ones((pm, bitmapRange)) # the first bit would always be 1, so not stored in this bitmap
        # in the beginning all states[c] = 1 so we should let the bitmap all be 1
        self.bitmapRange = bitmapRange
        self.diffbd = pDiffbd
        ceofx = np.arange(pm)
        self.sawtoffset = np.where(ceofx%2==0, 0.5, 0)
        self.offset = np.where(ceofx%2==0, 0.5, 0) + np.array(np.arange(pm), dtype=np.float64)/(2*pm)
        self.a = np.sum(np.power(self.q, -self.states - self.offset))
        self.runningColSingStr += ["blw"+str(i)+"-bit" for i in range(bitmapRange)]

    def update(self, c, k, t):
        if k > self.states[c] or self.states[c]-self.bitmapRange <= k < self.states[c]:
            oldstate = self.states[c]
            if k < self.states[c]:
                if self.bitmap[c, oldstate - k - 1] == 0:
                    self.updateMtg()
                    self.bitmap[c, oldstate - k - 1] = 1
                    self.updateA(self.a - (1-1/self.q)*(np.power(self.q, -k)))
                    self.updateSnapshot(t, c, k, [])
                    self.runningHistNewcontent = self.bitmap
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
                for i in range(1, CurtainUpbd):
                    if c - i >= 0 and self.states[c-i] + self.sawtoffset[c-i] < k + self.sawtoffset[c] - i * self.diffbd:
                        oldCMIstate = self.states[c-i]
                        self.states[c-i] = k-i*self.diffbd + self.sawtoffset[c] - self.sawtoffset[c-i]
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
                    if c + i < self.m and self.states[c+i] + self.sawtoffset[c+i] < k + self.sawtoffset[c] - i * self.diffbd:
                        oldCPIstate = self.states[c+i]
                        self.states[c+i] = k-i*self.diffbd + self.sawtoffset[c] - self.sawtoffset[c-i]
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
                    if k - i * self.diffbd < 0:
                        break
                probBitmap = np.vstack(tuple((1 + np.arange(self.bitmapRange)- self.states[i] - self.offset[i]) for i in range(self.m)))
                remainingAreaBitmap = np.sum(np.multiply(1 - self.bitmap, np.power(self.q, probBitmap))) * (1 - 1/self.q)
                self.updateA(remainingAreaBitmap + np.sum(np.power(self.q, -self.states - self.offset)))
                self.updateSnapshot(t, c, k, [])
                self.runningHistNewcontent = self.bitmap
                return True, cList
        else:
            return False, []

    def refresh(self):
        super(CurtainPCSASketch, self).refresh()
        self.bitmap = np.ones(self.bitmap.shape)
        self.a = np.sum(np.power(self.q, -self.states - self.offset))

    def updategen(self):
        remainingArea = np.float64(self.a/self.m)
        if remainingArea < 1e-8:
            deltat = np.float64(np.random.exponential(1/remainingArea))
        else:
            deltat = np.float64(np.random.geometric(remainingArea))
        probBitmap = np.vstack(tuple((1 + np.arange(self.bitmapRange)-self.states[i]-self.offset[i]) for i in range(self.m)))
        remainingAreaBitmap = np.sum(np.multiply(1 - self.bitmap, np.power(self.q, probBitmap)), axis=1) * (1 - 1/self.q)
        probList = np.power(1/self.q, self.states + self.offset) + remainingAreaBitmap
        probListsum = np.sum(probList)
        c = np.random.choice(np.arange(self.m), p=probList/probListsum)
        probList_ = np.array([np.power(1/self.q, self.states[c]+self.offset[c]), remainingAreaBitmap[c]])
        k_ = np.random.choice([0, 1], p=probList_/(np.sum(probList_)))
        if k_ == 0:
            k = self.states[c] + np.random.geometric(1-1/self.q)
        else:
            bitmapProblist = np.multiply(1-self.bitmap[c], np.power(self.q, np.arange(self.bitmapRange)))
            k0 = np.random.choice(np.arange(self.bitmapRange), p=bitmapProblist/(np.sum(bitmapProblist)))
            k = self.states[c] - 1 - k0
        return np.float64(self.t+deltat), c, k


class CurtainStarSketch(Sketch):
    def __init__(self, pm, pq, pN, pUpbd, pcolor='green', pname="CtnStar"):
        mpname = "-".join([pname, str(pm), str(pq), str(pUpbd)])
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


class CurtainSecondHighSketch(Sketch):
    # this sketch ensures the difference of adjacent counters <= pDiffbd.
    def __init__(self, pm, pq, pN, pDiffbd, pSecondbd, pcolor='orange', pname="CtnSecondHigh"):
        mpname = "-".join([pname, str(pm), str(pq), str(pDiffbd), str(pSecondbd)])
        super(CurtainSecondHighSketch, self).__init__(pm, pq, pN, pcolor, mpname, prunhistLenNew=1)
        self.diffbd = pDiffbd
        self.runningColSingStr += ["second"]
        ceofx = np.arange(pm)
        self.sawtoffset = np.where(ceofx%2==0, 0.5, 0)
        self.offset = np.where(ceofx%2==0, 0.5, 0) + np.array(np.arange(pm), dtype=np.float64)/(2*pm)
        self.secondbd = np.int64(pSecondbd)
        self.secondstates = np.zeros(self.m, dtype=np.int64)
        self.a = np.sum(np.power(self.q, -self.states - self.offset))

    def update(self, c, k, t):
        if k > self.states[c]:
            cList = [c]
            self.updateMtg()
            self.states[c] = k
            self.secondstates[c] = max(self.secondstates[c], self.states[c] - self.secondbd)
            for i in range(1, CurtainUpbd):
                if c - i >= 0 and (self.states[c]+self.sawtoffset[c]-self.states[c-i]-self.sawtoffset[c-i] > self.diffbd*i):
                    self.states[c-i] = k-i*self.diffbd + self.sawtoffset[c] - self.sawtoffset[c-i]
                    self.secondstates[c-i] = max(self.secondstates[c-i], self.states[c-i] - self.secondbd)
                    cList.append(c-i)
                if c + i < self.m and self.states[c+i] + self.sawtoffset[c+i] < k + self.sawtoffset[c] - i * self.diffbd:
                    self.states[c+i] = k-i*self.diffbd + self.sawtoffset[c] - self.sawtoffset[c-i]
                    self.secondstates[c+i] = max(self.secondstates[c+i], self.states[c+i] - self.secondbd)
                    cList.append(c+i)
                if k - i * self.diffbd < 0:
                    break
            remainingAreaSecond = np.maximum(0, np.power(self.q, -self.secondstates-self.offset-1) - np.power(self.q, -self.states-self.offset))
            self.updateA(np.sum(np.power(self.q, -self.states-self.offset)) + np.sum(remainingAreaSecond))
            self.updateSnapshot(t, c, k, [])
            self.runningHistNewcontent = self.secondstates
            return True, cList
        elif self.secondstates[c] < k < self.states[c]:
            self.secondstates[c] = k
            self.updateMtg()
            remainingAreaSecond = np.maximum(0, np.power(self.q, -self.secondstates-self.offset-1) - np.power(self.q, -self.states-self.offset))
            self.updateA(np.sum(np.power(self.q, -self.states-self.offset)) + np.sum(remainingAreaSecond))
            self.updateSnapshot(t, c, k, [])
            self.runningHistNewcontent = self.secondstates
            return True, [c]
        else:
            return False, []

    def updategen(self):
        remainingArea = np.float64(self.a/self.m)
        if remainingArea < 1e-8:
            deltat = np.float64(np.random.exponential(1/remainingArea))
        else:
            deltat = np.float64(np.random.geometric(remainingArea))
        remainingAreaSecond = np.maximum(0, np.power(self.q, -self.secondstates-self.offset-1) - np.power(self.q, -self.states-self.offset))
        probList = np.power(1/self.q, self.states + self.offset) + remainingAreaSecond
        c = np.random.choice(np.arange(self.m), p=probList/np.sum(probList))

        probList_c = np.array([np.power(1/self.q, self.states[c]+self.offset[c]), remainingAreaSecond[c]])
        k_ = np.random.choice([0, 1], p=probList_c/(np.sum(probList_c)))
        if k_ == 0 or probList_c[1] == 0:
            k = self.states[c] + np.random.geometric(1-1/self.q)
        else:
            assert self.secondstates[c] <= self.states[c] - 2
            secondRange = np.arange(self.secondstates[c] + 1, self.states[c])
            prob_secondrange = np.power(self.q, -secondRange)
            k = np.random.choice(secondRange, p=prob_secondrange/(np.sum(prob_secondrange)))
        return np.float64(self.t+deltat), c, k


class LazyCurtainPCSASketch(Sketch):
    # this sketch ensures the difference of adjacent counters <= pDiffbd.
    # this sketch has not finished.
    def __init__(self, pm, pq, pN, pDiffbd, bitmapRange, pcolor='orange', pname="LazyCtnPCSA"):
        mpname = "-".join([pname, str(pm), str(pq), str(pDiffbd), str(bitmapRange)])
        super(LazyCurtainPCSASketch, self).__init__(pm, pq, pN, pcolor, mpname, prunhistLenNew=bitmapRange)
        self.states += bitmapRange
        self.bitmap = np.zeros((pm, bitmapRange))
        self.bitmapRange = bitmapRange
        self.diffbd = pDiffbd
        ceofx = np.arange(pm)
        self.sawtoffset = np.where(ceofx % 2 == 0, 0.5, 0)
        self.offset = np.where(ceofx % 2 == 0, 0.5, 0) + np.array(np.arange(pm), dtype=np.float64) / (2 * pm)
        self.a = np.sum(np.power(self.q, -self.offset))
        self.runningColSingStr += [str(i) + "-th bit" for i in range(bitmapRange)]

    def update(self, c, k, t):
        if k >= self.states[c] - self.bitmapRange + 1:
            oldstate = self.states[c]
            if k <= self.states[c]:
                if self.bitmap[c, oldstate - k] == 0:
                    self.updateMtg()
                    self.bitmap[c, oldstate - k] = 1
                    self.updateA(self.a - (1 - 1 / self.q) * (np.power(self.q, -k+1-self.offset[c])))
                    self.updateSnapshot(t, c, k, [])
                    self.runningHistNewcontent = self.bitmap
                    return True, [c]
                else:
                    return False, []
            else:
                self.states[c] = k
                cList = [c]
                self.updateMtg()
                newkbitmap = np.zeros(self.bitmapRange)
                newkbitmap[0] = 1
                if k - oldstate < self.bitmapRange:
                    newkbitmap[k-oldstate:self.bitmapRange] = (self.bitmap[c])[0:oldstate+self.bitmapRange-k]
                self.bitmap[c] = newkbitmap
                for i in range(1, CurtainUpbd):
                    if c - i >= 0 and self.states[c - i] + self.sawtoffset[c - i] < k + self.sawtoffset[c] - i * self.diffbd:
                        oldCMIstate = self.states[c - i]
                        self.states[c - i] = k - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c - i]
                        newCMIstate = self.states[c - i]
                        cList.append(c - i)
                        newCMIbitmap = np.zeros(self.bitmapRange)
                        if newCMIstate - oldCMIstate < self.bitmapRange:
                            newCMIbitmap[newCMIstate-oldCMIstate:self.bitmapRange] = (self.bitmap[c-i])[0:oldCMIstate+self.bitmapRange-newCMIstate]
                        self.bitmap[c - i] = newCMIbitmap
                    if c + i < self.m and self.states[c + i] + self.sawtoffset[c + i] < k + self.sawtoffset[c] - i * self.diffbd:
                        oldCPIstate = self.states[c + i]
                        self.states[c + i] = k - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c - i]
                        newCPIstate = self.states[c + i]
                        cList.append(c + i)
                        newCPIbitmap = np.zeros(self.bitmapRange)
                        if newCPIstate - oldCPIstate < self.bitmapRange:
                            newCPIbitmap[newCPIstate-oldCPIstate:self.bitmapRange] = (self.bitmap[c+i])[0:oldCPIstate+self.bitmapRange-newCPIstate]
                        self.bitmap[c + i] = newCPIbitmap
                    if k - i * self.diffbd < 0:
                        break
                probBitmap = np.vstack(tuple((1 + np.arange(self.bitmapRange) - self.states[i] - self.offset[i]) for i in range(self.m)))
                remainingAreaBitmap = np.sum(np.multiply(1 - self.bitmap, np.power(self.q, probBitmap))) * (1 - 1 / self.q)
                self.updateA(remainingAreaBitmap + np.sum(np.power(self.q, -self.states - self.offset)))
                self.updateSnapshot(t, c, k, [])
                self.runningHistNewcontent = self.bitmap
                return True, cList
        else:
            return False, []

    def refresh(self):
        super(LazyCurtainPCSASketch, self).refresh()
        self.bitmap = np.zeros(self.bitmap.shape)
        self.states += self.bitmapRange
        self.a = np.sum(np.power(self.q, -self.offset))

    def updategen(self):
        remainingArea = np.float64(self.a / self.m)
        if remainingArea < 1e-8:
            deltat = np.float64(np.random.exponential(1 / remainingArea))
        else:
            deltat = np.float64(np.random.geometric(remainingArea))
        probBitmap = np.vstack(tuple((1+np.arange(self.bitmapRange) - self.states[i] - self.offset[i]) for i in range(self.m)))
        remainingAreaBitmap = np.sum(np.multiply(1 - self.bitmap, np.power(self.q, probBitmap)), axis=1) * (1 - 1 / self.q)
        probList = np.power(1 / self.q, self.states + self.offset) + remainingAreaBitmap
        c = np.random.choice(np.arange(self.m), p=probList / np.sum(probList))
        probList_ = np.array([np.power(1 / self.q, self.states[c] + self.offset[c]), remainingAreaBitmap[c]])
        k_ = np.random.choice([0, 1], p=probList_ / (np.sum(probList_)))
        if k_ == 0:
            k = self.states[c] + np.random.geometric(1 - 1 / self.q)
        else:
            bitmapProblist = np.multiply(1 - self.bitmap[c], np.power(self.q, np.arange(self.bitmapRange)))
            k0 = np.random.choice(np.arange(self.bitmapRange), p=bitmapProblist / (np.sum(bitmapProblist)))
            k = self.states[c] - k0
        return np.float64(self.t + deltat), c, k


class AdaLazyCurtainPCSASketch(Sketch):
    def __init__(self, pm, pq, pN, pDiffbd, pfbitmapRange, pcolor='orange', pname="AdaLazyCtnPCSA"):
        bitmapRange = pfbitmapRange + 1
        mpname = "-".join([pname, str(pm), str(pq), str(pDiffbd), str(bitmapRange)])
        super(AdaLazyCurtainPCSASketch, self).__init__(pm, pq, pN, pcolor, mpname, prunhistLenNew=bitmapRange)
        self.states += bitmapRange - 1
        self.bitmap = np.zeros((pm, bitmapRange))
        self.bitmap[:, -1] = 1
        self.bitmapRange = bitmapRange
        self.diffbd = pDiffbd
        ceofx = np.arange(pm)
        self.sawtoffset = np.where(ceofx % 2 == 0, 0.5, 0)
        self.offset = np.where(ceofx % 2 == 0, 0.5, 0) + np.array(np.arange(pm), dtype=np.float64) / (2 * pm)
        self.a = np.sum(np.power(self.q, -self.offset))
        self.runningColSingStr += [str(i) + "-th bit" for i in range(bitmapRange)]
        self.updateA(self.a)

    def update(self, c, k, t):
        if k >= self.states[c] - self.bitmapRange + 1:
            oldstate = self.states[c]
            if k <= self.states[c]:
                if self.bitmap[c, oldstate - k] == 0:
                    self.updateMtg()
                    self.bitmap[c, oldstate - k] = 1
                    self.updateA(self.a - (1 - 1 / self.q) * (np.power(self.q, -k+1-self.offset[c])))
                    self.updateSnapshot(t, c, k, [])
                    self.runningHistNewcontent = self.bitmap
                    return True, [c]
                else:
                    return False, []
            else:
                self.states[c] = k
                cList = [c]
                self.updateMtg()
                newkbitmap = np.zeros(self.bitmapRange)
                newkbitmap[0] = 1
                if k - oldstate < self.bitmapRange:
                    newkbitmap[k-oldstate:self.bitmapRange] = (self.bitmap[c])[0:oldstate+self.bitmapRange-k]
                self.bitmap[c] = newkbitmap
                for i in range(1, CurtainUpbd):
                    if c - i >= 0 and self.states[c - i] + self.sawtoffset[c - i] < k + self.sawtoffset[c] - i * self.diffbd:
                        oldCMIstate = self.states[c - i]
                        self.states[c - i] = k - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c - i]
                        newCMIstate = self.states[c - i]
                        cList.append(c - i)
                        newCMIbitmap = np.zeros(self.bitmapRange)
                        if newCMIstate - oldCMIstate < self.bitmapRange:
                            newCMIbitmap[newCMIstate-oldCMIstate:self.bitmapRange] = (self.bitmap[c-i])[0:oldCMIstate+self.bitmapRange-newCMIstate]
                        newCMIbitmap[-1] = 1
                        self.bitmap[c - i] = newCMIbitmap
                    if c + i < self.m and self.states[c + i] + self.sawtoffset[c + i] < k + self.sawtoffset[c] - i * self.diffbd:
                        oldCPIstate = self.states[c + i]
                        self.states[c + i] = k - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c - i]
                        newCPIstate = self.states[c + i]
                        cList.append(c + i)
                        newCPIbitmap = np.zeros(self.bitmapRange)
                        if newCPIstate - oldCPIstate < self.bitmapRange:
                            newCPIbitmap[newCPIstate-oldCPIstate:self.bitmapRange] = (self.bitmap[c+i])[0:oldCPIstate+self.bitmapRange-newCPIstate]
                        newCPIbitmap[-1] = 1
                        self.bitmap[c + i] = newCPIbitmap
                    if k - i * self.diffbd < 0:
                        break
                probBitmap = np.vstack(tuple((1 + np.arange(self.bitmapRange) - self.states[i] - self.offset[i]) for i in range(self.m)))
                remainingAreaBitmap = np.sum(np.multiply(1 - self.bitmap, np.power(self.q, probBitmap))) * (1 - 1 / self.q)
                self.updateA(remainingAreaBitmap + np.sum(np.power(self.q, -self.states - self.offset)))
                self.updateSnapshot(t, c, k, [])
                self.runningHistNewcontent = self.bitmap
                return True, cList
        else:
            return False, []

    def refresh(self):
        super(AdaLazyCurtainPCSASketch, self).refresh()
        self.bitmap = np.zeros(self.bitmap.shape)
        self.bitmap[:, -1] = 1
        self.states += self.bitmapRange - 1
        self.a = np.sum(np.power(self.q, -self.offset))
        self.updateA(self.a)

    def updategen(self):
        remainingArea = np.float64(self.a / self.m)
        if remainingArea < 1e-8:
            deltat = np.float64(np.random.exponential(1 / remainingArea))
        else:
            deltat = np.float64(np.random.geometric(remainingArea))
        probBitmap = np.vstack(tuple((1+np.arange(self.bitmapRange) - self.states[i] - self.offset[i]) for i in range(self.m)))
        remainingAreaBitmap = np.sum(np.multiply(1 - self.bitmap, np.power(self.q, probBitmap)), axis=1) * (1 - 1 / self.q)
        probList = np.power(1 / self.q, self.states + self.offset) + remainingAreaBitmap
        c = np.random.choice(np.arange(self.m), p=probList / np.sum(probList))
        probList_ = np.array([np.power(1 / self.q, self.states[c] + self.offset[c]), remainingAreaBitmap[c]])
        k_ = np.random.choice([0, 1], p=probList_ / (np.sum(probList_)))
        if k_ == 0:
            k = self.states[c] + np.random.geometric(1 - 1 / self.q)
        else:
            bitmapProblist = np.multiply(1 - self.bitmap[c], np.power(self.q, np.arange(self.bitmapRange)))
            k0 = np.random.choice(np.arange(self.bitmapRange), p=bitmapProblist / (np.sum(bitmapProblist)))
            k = self.states[c] - k0
        return np.float64(self.t + deltat), c, k


class AdaLazyCtnPCSA_Ctn2bit_Board1bit_Sketch(Sketch):
    def __init__(self, pm, pq, pN, pverbos=0, pcolor='orange', pname="AdaLazyCtnPCSA"):
        mpname = "-".join([pname, str(pm), str(pq), str(1.5), str(1)])
        super(AdaLazyCtnPCSA_Ctn2bit_Board1bit_Sketch, self).__init__(pm, pq, pN, pcolor, mpname, prunhistLenNew=2)
        self.states += 1
        self.bitmap = np.ones(pm) # 1 for not chosen, 0 for already appeared
        self.tension = np.zeros(pm) # 1 for not in tension, 0 for in tension
        self.diffbd = 1.5
        ceofx = np.arange(pm)
        self.sawtoffset = np.where(ceofx % 2 == 0, 0.5, 0)
        self.offset = np.where(ceofx % 2 == 0, 0.5, 0) + np.array(np.arange(pm), dtype=np.float64) / (2 * pm)
        self.a = np.sum(np.power(self.q, -self.offset))
        self.runningColSingStr += ["bit below", "tension"]
        self.updateA(self.a)
        self.verbos = pverbos

    def update(self, c, k, t):
        if k > self.states[c]:
            cList = []
            if self.verbos != 0:
                cList.append(c)
            self.updateMtg()
            if k == self.states[c] + 1:
                if self.tension[c] == 1:
                    self.bitmap[c] = 0
            else:
                self.bitmap[c] = 1
            self.tension[c] = 1
            self.states[c] = k

            for i in range(1, CurtainUpbd):
                if c - i >= 0 and self.states[c - i] + self.sawtoffset[c - i] < k + self.sawtoffset[c] - i * self.diffbd:
                    self.states[c - i] = k - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c - i]
                    if self.verbos != 0:
                        cList.append(c - i)
                    self.bitmap[c - i] = 1
                    self.tension[c - i] = 0
                if c + i < self.m and self.states[c + i] + self.sawtoffset[c + i] < k + self.sawtoffset[c] - i * self.diffbd:
                    self.states[c + i] = k - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c - i]
                    if self.verbos != 0:
                        cList.append(c + i)
                    self.bitmap[c + i] = 1
                    self.tension[c + i] = 0
                if k - i * self.diffbd < 0:
                    break
            belowProbSum = np.dot(np.power(1/self.q, self.states + self.offset - self.tension - 1), self.bitmap) * (1 - 1/self.q)
            self.updateA(belowProbSum + np.sum(np.power(1/self.q, self.states + self.offset)))
            if self.verbos != 0:
                self.updateSnapshot(t, c, k, [])
                self.runningHistNewcontent = np.vstack((self.bitmap, self.tension)).transpose()
            else:
                self.t = t
            return True, cList
        elif k == self.states[c] - self.tension[c] and self.bitmap[c] == 1:
            self.updateMtg()
            self.bitmap[c] = 0
            self.updateA(self.a - (1 - 1 / self.q) * (np.power(self.q, -k + 1 - self.offset[c])))
            if self.verbos != 0:
                self.updateSnapshot(t, c, k, [])
                self.runningHistNewcontent = np.vstack((self.bitmap, self.tension)).transpose()
            else:
                self.t = t
            return True, [c]
        else:
            return False, []

    def refresh(self):
        super(AdaLazyCtnPCSA_Ctn2bit_Board1bit_Sketch, self).refresh()
        self.bitmap = np.ones(self.bitmap.shape)
        self.states += 1
        self.tension = np.zeros(self.tension.shape)
        self.a = np.sum(np.power(self.q, -self.offset))
        self.updateA(self.a)

    def updategen(self):
        if self.rega < 1e-8:
            deltat = np.float64(np.random.exponential(self.invrega))
        else:
            deltat = np.float64(np.random.geometric(self.rega))
        belowProb = np.multiply(np.power(1/self.q, self.states + self.offset - self.tension - 1), self.bitmap) * (1 - 1/self.q)
        upperProb = np.power(1/self.q, self.states + self.offset)
        belowSum = np.sum(belowProb)
        upperSum = np.sum(upperProb)
        upOrbelow = np.random.choice([0, 1], p=[belowSum/(belowSum+upperSum), upperSum/(belowSum+upperSum)])
        if upOrbelow == 0:
            c = np.random.choice(np.arange(self.m), p=belowProb/belowSum)
            k = self.states[c] - self.tension[c]
        else:
            c = np.random.choice(np.arange(self.m), p=upperProb/upperSum)
            k = self.states[c] + np.random.geometric(1 - 1/self.q)
        return np.float64(self.t + deltat), c, k


class GroupCurtainPCSA(Sketch):
    def __init__(self, pm, pq, pN, pDiffbd, pfbitmapRange, pgroupSize=3, pverbos=0, pCR=12, pcolor='orange', pname="GrpCtnPCSA"):
        assert pm % (2*pgroupSize) == 0
        self._m = pm/pgroupSize
        mpname = "-".join([pname, str(pm), str(pq), str(pDiffbd), str(pfbitmapRange), str(pgroupSize)])
        self.newcontentRange = pCR
        super(GroupCurtainPCSA, self).__init__(pm, pq, pN, pcolor, mpname, prunhistLenNew=pCR)
        self.states += pfbitmapRange - 1
        self.bitmap = np.ones((pm, PCSAUpbd)) # 0 for seen, 1 for not seen, remaining area
        # position i: (1-1/q)(1/q)^i; e.g. 0: 1-1/q; 1: 1/q-1/q^2
        self.bitmapRange = pfbitmapRange
        self.diffbd = pDiffbd
        self.g = pgroupSize
        self.verbos = pverbos
        ceofx = np.arange(pm)
        self.sawtoffset = np.where((ceofx//pgroupSize) % 2 == 0, 0.5, 0)
        self.offset = np.where((ceofx//pgroupSize) % 2 == 0, 0.5, 0) + np.array(np.arange(pm), dtype=np.float64) / (2 * pm)
        self.a = np.sum(np.power(self.q, -self.offset))
        self.runningColSingStr += [str(i) + "-th bit" for i in range(pCR)]
        self.updateA(self.a)
        self.probbitmap = np.multiply(np.power(1/self.q, np.zeros(self.bitmap.shape)+self.offset.reshape(self.m, 1)), np.power(1/self.q, np.arange(PCSAUpbd))*(1-1/self.q))
        self.abovePCSAUpbd_aList = np.power(1/self.q, PCSAUpbd + self.offset)
        self.abovePCSAUpbd_a = np.sum(self.abovePCSAUpbd_aList)

    def update(self, c, k, t):
        g = self.g
        if k > self.states[c]:
            _c = c // g
            cList = [_c * g + i for i in range(g)]
            self.updateMtg()
            self.states[_c*g:(_c+1)*g] = k
            self.bitmap[c, k] = 0
            for _i in range(1, CurtainUpbd):
                if _c-_i>=0 and self.states[(_c-_i)*g]+self.sawtoffset[(_c-_i)*g]<k+self.sawtoffset[_c*g]-_i*self.diffbd:
                    self.states[(_c-_i)*g:(_c-_i+1)*g]=k-_i*self.diffbd+self.sawtoffset[_c*g]-self.sawtoffset[(_c-_i)*g]
                    cList += [(_c-_i)*g+i for i in range(g)]
                if _c+_i<self._m and self.states[(_c+_i)*g]+self.sawtoffset[(_c+_i)*g]<k+self.sawtoffset[_c*g]-_i*self.diffbd:
                    self.states[(_c+_i)*g:(_c+_i+1)*g]=k-_i*self.diffbd+self.sawtoffset[_c*g]-self.sawtoffset[(_c+_i)*g]
                    cList += [(_c+_i)*g+i for i in range(g)]
                if k - _i * self.diffbd < 0:
                    break
            for i in cList:
                if self.states[i] - self.bitmapRange + 1 > 0:
                    self.bitmap[i, 0:(self.states[i]-self.bitmapRange+1)] = 0
            self.updateA(np.sum(np.multiply(self.bitmap, self.probbitmap)) + self.abovePCSAUpbd_a)
            if self.verbos != 0:
                self.updateSnapshot(t, c, k, [])
                self.runningHistNewcontent = self.bitmap[:, 0:self.newcontentRange]
            else:
                self.t = t
            return True, cList
        elif k >= self.states[c] - self.bitmapRange + 1 and self.bitmap[c, k] == 1:
            self.updateMtg()
            self.bitmap[c, k] = 0
            self.updateA(self.a - self.probbitmap[c, k])
            if self.verbos != 0:
                self.updateSnapshot(t, c, k, [])
                self.runningHistNewcontent = self.bitmap[:, 0:self.newcontentRange]
            else:
                self.t = t
            return True, [c]
        else:
            return False, []

    def refresh(self):
        super(GroupCurtainPCSA, self).refresh()
        self.bitmap = np.ones(self.bitmap.shape)
        self.states += self.bitmapRange - 1
        self.a = np.sum(np.power(self.q, -self.offset))
        self.updateA(self.a)

    def updategen(self):
        remainingArea = np.float64(self.a / self.m)
        if remainingArea < 1e-8:
            deltat = np.float64(np.random.exponential(1 / remainingArea))
        else:
            deltat = np.float64(np.random.geometric(remainingArea))

        probBitmap = np.multiply(self.bitmap, self.probbitmap)
        prob_c = np.sum(probBitmap, axis=1) + self.abovePCSAUpbd_aList
        c = np.random.choice(np.arange(self.m), p=prob_c / np.sum(prob_c))
        probList_ = np.hstack((probBitmap[c], self.abovePCSAUpbd_aList[c]))
        k = np.random.choice(np.arange(PCSAUpbd+1), p=probList_/(np.sum(probList_)))
        if k == PCSAUpbd:
            k += np.random.geometric(1 - 1 / self.q)
        return np.float64(self.t + deltat), c, k


class SecondHighCurtainSketch(Sketch):
    # this sketch ensures the difference of adjacent counters <= pDiffbd.
    def __init__(self, pm, pq, pN, pDiffbd, pSecondbd, pverbos=0, pcolor='orange', pname="SecondHighCtn"):
        mpname = "-".join([pname, str(pm), str(pq), str(pDiffbd), str(pSecondbd)])
        super(SecondHighCurtainSketch, self).__init__(pm, pq, pN, pcolor, mpname, prunhistLenNew=2)
        self.diffbd = pDiffbd
        self.runningColSingStr += ["first", "tension"]
        ceofx = np.arange(pm)
        self.sawtoffset = np.where(ceofx%2==0, 0.5, 0)
        self.offset = np.where(ceofx%2==0, 0.5, 0) + np.array(np.arange(pm), dtype=np.float64)/(2*pm)
        self.secondbd = np.int64(pSecondbd)
        self.firststates = np.zeros(pm, dtype=np.int64)
        self.tension = np.zeros(pm, dtype=np.int64) # 0 is in tension, 1 is not in tension
        # when tension=0, first-second in [0, scbd-1], when tension=1, first-second in [1, scbd]
        self.verbos = pverbos
        self.updateA(np.sum(np.power(self.q, -self.states - self.offset)))

    def update(self, c, k, t):
        if (k > self.firststates[c] > self.states[c]) or (self.firststates[c] == self.states[c] and k > self.states[c] + self.secondbd + self.tension[c]):
            cList = [c]
            self.updateMtg()
            self.tension[c] = 1
            self.states[c] = max(k - self.secondbd - self.tension[c], self.firststates[c])
            self.firststates[c] = k
            for i in range(1, CurtainUpbd):
                if c - i >= 0 and self.states[c-i] + self.sawtoffset[c-i] < self.states[c] + self.sawtoffset[c] - i * self.diffbd:
                    self.tension[c-i] = 0
                    self.states[c-i] = self.states[c] - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c-i]
                    self.firststates[c-i] = max(self.states[c-i], self.firststates[c-i])
                    cList.append(c-i)
                if c + i < self.m and self.states[c+i] + self.sawtoffset[c+i] < self.states[c]+ self.sawtoffset[c] - i * self.diffbd:
                    self.tension[c+i] = 0
                    self.states[c+i] = self.states[c] - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c+i]
                    self.firststates[c+i] = max(self.firststates[c+i], self.states[c+i])
                    cList.append(c+i)
                if k - i * self.diffbd < 0:
                    break
            fsoverlap = np.where(self.states == self.firststates, 0, np.power(self.q, -self.firststates-self.offset))*(1-1/self.q)
            self.updateA(np.sum(np.power(self.q, -self.states-self.offset))-np.sum(fsoverlap))
            if self.verbos != 0:
                self.updateSnapshot(t, c, k, [])
                self.runningHistNewcontent = np.vstack((self.firststates, self.tension)).transpose()
            else:
                self.t = t
            return True, cList
        elif self.states[c] < k <= self.states[c] + self.secondbd + self.tension[c] and self.firststates[c] == self.states[c]:
            cList = [c]
            self.updateMtg()
            self.firststates[c] = k
            fsoverlap = np.where(self.states == self.firststates, 0, np.power(self.q, -self.firststates - self.offset)) * (1 - 1 / self.q)
            self.updateA(np.sum(np.power(self.q, -self.states - self.offset)) - np.sum(fsoverlap))
            if self.verbos != 0:
                self.updateSnapshot(t, c, k, [])
                self.runningHistNewcontent = np.vstack((self.firststates, self.tension)).transpose()
            else:
                self.t = t
            return True, cList
        elif self.states[c] < k < self.firststates[c]:
            cList = [c]
            self.states[c] = k
            self.tension[c] = 1
            self.updateMtg()
            for i in range(1, CurtainUpbd):
                if c - i >= 0 and self.states[c-i] + self.sawtoffset[c-i] < self.states[c] + self.sawtoffset[c] - i * self.diffbd:
                    self.tension[c-i] = 0
                    self.states[c-i] = self.states[c] - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c-i]
                    self.firststates[c-i] = max(self.states[c-i], self.firststates[c-i])
                    cList.append(c-i)
                if c + i < self.m and self.states[c+i] + self.sawtoffset[c+i] < self.states[c]+ self.sawtoffset[c] - i * self.diffbd:
                    self.tension[c+i] = 0
                    self.states[c+i] = self.states[c] - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c+i]
                    self.firststates[c+i] = max(self.firststates[c+i], self.states[c+i])
                    cList.append(c+i)
                if k - i * self.diffbd < 0:
                    break
            fsoverlap = np.where(self.states == self.firststates, 0, np.power(self.q, -self.firststates - self.offset)) * (1 - 1 / self.q)
            self.updateA(np.sum(np.power(self.q, -self.states - self.offset)) - np.sum(fsoverlap))
            if self.verbos != 0:
                self.updateSnapshot(t, c, k, [])
                self.runningHistNewcontent = np.vstack((self.firststates, self.tension)).transpose()
            else:
                self.t = t
            return True, cList
        else:
            return False, []

    def refresh(self):
        super(SecondHighCurtainSketch, self).refresh()
        self.firststates = np.zeros(self.firststates.shape, dtype=np.int64)
        self.tension = np.zeros(self.tension.shape, dtype=np.int64)

    def updategen(self):
        remainingArea = np.float64(self.a/self.m)
        if remainingArea < 1e-8:
            deltat = np.float64(np.random.exponential(1/remainingArea))
        else:
            deltat = np.float64(np.random.geometric(remainingArea))
        fsoverlap = np.where(self.states == self.firststates, 0, np.power(self.q, 1 - self.firststates - self.offset))*(1 - 1 / self.q)
        probList = np.power(self.q, -self.states - self.offset) - fsoverlap
        c = np.random.choice(np.arange(self.m), p=probList/np.sum(probList))
        lower = probList[c]-np.power(1/self.q, self.firststates[c]+self.offset[c]) if self.firststates[c] not in (self.states[c], self.states[c]+1) else 0
        probList_c = np.array([lower, np.power(1/self.q, self.firststates[c]+self.offset[c])], dtype=np.float64)
        k_ = np.random.choice([0, 1], p=probList_c/(np.sum(probList_c)))
        if k_ == 1:
            k = self.firststates[c] + np.random.geometric(1-1/self.q)
        else:
            assert self.states[c] <= self.firststates[c] - 2
            secondRange = np.arange(self.states[c] + 1, self.firststates[c])
            prob_secondrange = np.power(self.q, -secondRange)
            k = np.random.choice(secondRange, p=prob_secondrange/(np.sum(prob_secondrange)))
        return np.float64(self.t+deltat), c, k


class DoubleCurtainSketch(Sketch):
    # this sketch ensures the difference of adjacent counters <= pDiffbd.
    def __init__(self, pm, pq, pN, pDiffbd, pverbos=0, pcolor='orange', pname="DoubleCtn"):
        mpname = "-".join([pname, str(pm), str(pq), str(pDiffbd)])
        super(DoubleCurtainSketch, self).__init__(pm, pq, pN, pcolor, mpname, prunhistLenNew=1)
        self.diffbd = pDiffbd
        self.runningColSingStr += ["first"]
        ceofx = np.arange(pm)
        self.sawtoffset = np.where(ceofx%2==0, 0.5, 0)
        self.offset = np.where(ceofx%2==0, 0.5, 0) + np.array(np.arange(pm), dtype=np.float64)/(2*pm)
        self.firststates = np.zeros(pm, dtype=np.int64)
        self.verbos = pverbos
        self.updateA(np.sum(np.power(self.q, -self.states - self.offset)))

    def update(self, c, k, t):
        if k > self.firststates[c]:
            cList = [c]
            self.updateMtg()
            self.states[c] = self.firststates[c]
            self.firststates[c] = k
            for i in range(1, CurtainUpbd):
                if c - i >= 0 and self.states[c-i] + self.sawtoffset[c-i] < self.states[c] + self.sawtoffset[c] - i * self.diffbd:
                    self.states[c-i] = self.states[c] - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c-i]
                    cList.append(c-i)
                if c - i >= 0 and self.firststates[c-i] + self.sawtoffset[c-i] < self.firststates[c] + self.sawtoffset[c] - i * self.diffbd:
                    self.firststates[c-i] = self.firststates[c] - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c-i]
                    if (c-i) not in cList:
                        cList.append(c-i)
                if c + i < self.m and self.states[c+i] + self.sawtoffset[c+i] < self.states[c]+ self.sawtoffset[c] - i * self.diffbd:
                    self.states[c+i] = self.states[c] - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c+i]
                    cList.append(c+i)
                if c + i < self.m and self.firststates[c+i] + self.sawtoffset[c+i] < self.firststates[c]+ self.sawtoffset[c] - i * self.diffbd:
                    self.firststates[c+i] = self.firststates[c] - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c+i]
                    if (c+i) not in cList:
                        cList.append(c+i)
                if k - i * self.diffbd < 0:
                    break
            fsoverlap = np.where(self.states == self.firststates, 0, np.power(self.q, -self.firststates-self.offset))*(1-1/self.q)
            self.updateA(np.sum(np.power(self.q, -self.states-self.offset))-np.sum(fsoverlap))
            if self.verbos != 0:
                self.updateSnapshot(t, c, k, [])
                self.runningHistNewcontent = self.firststates
            else:
                self.t = t
            return True, cList
        elif self.states[c] < k < self.firststates[c]:
            cList = [c]
            self.states[c] = k
            self.updateMtg()
            for i in range(1, CurtainUpbd):
                if c - i >= 0 and self.states[c-i] + self.sawtoffset[c-i] < self.states[c] + self.sawtoffset[c] - i * self.diffbd:
                    self.states[c-i] = self.states[c] - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c-i]
                    cList.append(c-i)
                if c + i < self.m and self.states[c+i] + self.sawtoffset[c+i] < self.states[c]+ self.sawtoffset[c] - i * self.diffbd:
                    self.states[c+i] = self.states[c] - i * self.diffbd + self.sawtoffset[c] - self.sawtoffset[c+i]
                    cList.append(c+i)
                if k - i * self.diffbd < 0:
                    break
            fsoverlap = np.where(self.states == self.firststates, 0, np.power(self.q, -self.firststates - self.offset)) * (1 - 1 / self.q)
            self.updateA(np.sum(np.power(self.q, -self.states - self.offset)) - np.sum(fsoverlap))
            if self.verbos != 0:
                self.updateSnapshot(t, c, k, [])
                self.runningHistNewcontent = self.firststates
            else:
                self.t = t
            return True, cList
        else:
            return False, []

    def refresh(self):
        super(DoubleCurtainSketch, self).refresh()
        self.firststates = np.zeros(self.firststates.shape, dtype=np.int64)

    def updategen(self):
        remainingArea = np.float64(self.a/self.m)
        if remainingArea < 1e-8:
            deltat = np.float64(np.random.exponential(1/remainingArea))
        else:
            deltat = np.float64(np.random.geometric(remainingArea))
        fsoverlap = np.where(self.states == self.firststates, 0, np.power(self.q, 1 - self.firststates - self.offset))*(1 - 1 / self.q)
        probList = np.power(self.q, -self.states - self.offset) - fsoverlap
        c = np.random.choice(np.arange(self.m), p=probList/np.sum(probList))
        lower = probList[c]-np.power(1/self.q, self.firststates[c]+self.offset[c]) if self.firststates[c] not in (self.states[c], self.states[c]+1) else 0
        probList_c = np.array([lower, np.power(1/self.q, self.firststates[c]+self.offset[c])], dtype=np.float64)
        k_ = np.random.choice([0, 1], p=probList_c/(np.sum(probList_c)))
        if k_ == 1:
            k = self.firststates[c] + np.random.geometric(1-1/self.q)
        else:
            assert self.states[c] <= self.firststates[c] - 2
            secondRange = np.arange(self.states[c] + 1, self.firststates[c])
            prob_secondrange = np.power(self.q, -secondRange)
            k = np.random.choice(secondRange, p=prob_secondrange/(np.sum(prob_secondrange)))
        return np.float64(self.t+deltat), c, k



# def updategen(usketch:Sketch):
#     if type(usketch) == CurtainPCSASketch:
#         assert hasattr(usketch, "offset")
#         assert hasattr(usketch, "bitmapRange")
#         assert hasattr(usketch, "bitmap")
#         remainingArea = np.float64(usketch.a/usketch.m)
#         if remainingArea < 1e-8:
#             deltat = np.float64(np.random.exponential(1/remainingArea))
#         else:
#             deltat = np.float64(np.random.geometric(remainingArea))
#         probBitmap = np.vstack(tuple((1 + np.arange(usketch.bitmapRange)-usketch.states[i]-usketch.offset[i]) for i in range(usketch.m)))
#         remainingAreaBitmap = np.sum(np.multiply(1 - usketch.bitmap, np.power(usketch.q, probBitmap)), axis=1) * (1 - 1/usketch.q)
#         probList = np.power(1/usketch.q, usketch.states + usketch.offset) + remainingAreaBitmap
#         probListsum = np.sum(probList)
#         c = np.random.choice(np.arange(usketch.m), p=probList/probListsum)
#         probList_ = np.array([np.power(1/usketch.q, usketch.states[c]+usketch.offset[c]), remainingAreaBitmap[c]])
#         k_ = np.random.choice([0, 1], p=probList_/(np.sum(probList_)))
#         if k_ == 0:
#             k = usketch.states[c] + np.random.geometric(1-1/usketch.q)
#         else:
#             bitmapProblist = np.multiply(1-usketch.bitmap[c], np.power(usketch.q, np.arange(usketch.bitmapRange)))
#             k0 = np.random.choice(np.arange(usketch.bitmapRange), p=bitmapProblist/(np.sum(bitmapProblist)))
#             k = usketch.states[c] - 1 - k0
#         return np.float64(usketch.t+deltat), c, k
#     remainingArea = np.float64(usketch.a / usketch.m)
#     if remainingArea < 1e-8:
#         deltat = np.float64(np.random.exponential(1/remainingArea))
#     else:
#         deltat = np.float64(np.random.geometric(remainingArea))
#     if hasattr(usketch, "offset"):
#         prob = np.power(1/usketch.q, usketch.states + usketch.offset)
#     else:
#         prob = np.power(1/usketch.q, usketch.states)
#     condprob = prob / np.sum(prob)
#     c = np.random.choice(np.arange(usketch.m), p=condprob)
#     # prob of at least k
#     # = sum_k^infty (1-(1-1/q))^(i-1)(1-1/q)
#     # = (1/q)^{k-1}-(1/q)^{k} + ...
#     # = (1/q)^(k-1) :
#     # now you are at k, so the prob of at least k+1 is 1/q^k
#     k = usketch.states[c] + np.random.geometric(1-1/usketch.q)
#     newt = np.float64(usketch.t+deltat)
#     return newt, c, k
