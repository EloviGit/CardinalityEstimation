# this program runs simulations for various sketches and the code is arranged nicely

import numpy as np
import pandas as pd
import tqdm
import utils as utl
import sketches as sk

MaxBit = 1200  # T11
BitperCounter = 4
m = int(MaxBit/BitperCounter)
N = 5000
SuperInfty = 1e6
Round = 500
Upbd = (2**BitperCounter) - 2
# Size = 511
# AcName = "ac393"
# AcNName = "ac511N"
# AdaFrac = 0.2

ToSave = True
SaveHistIni = 1

samplN = 600
expsamplx = np.array(np.arange(samplN+1), dtype=np.float64)/samplN * 6
samplx = np.power(10, expsamplx)

qList = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]

Sketches = [sk.CurtainSecondHighSketch(m, q, N, pDiffbd=1.5, pSecondbd=2) for q in qList]

# names = [sketch.name for sketch in Sketches]
# DeathSketches = [sketch for sketch in Sketches if hasattr(sketch, "DeadNum")]
# invRegAlldf = pd.DataFrame(np.array(np.zeros((samplN, len(names))), dtype=np.float64), columns=names)

for sketch in Sketches:
    SaveHist = SaveHistIni
    MtgAlldf = pd.DataFrame(np.array(np.zeros((samplN + 1, Round)), dtype=np.float64), columns=list(range(Round)))
    regAAlldf = pd.DataFrame(np.array(np.zeros((samplN+1, Round)), dtype=np.float64), columns=list(range(Round)))
    print("Currently running Sketch"+sketch.name)
    for r in tqdm.tqdm(range(Round)):
    #for r in range(Round):
        tosaveRunHist = (SaveHist > 0)
        SketchReachedSupInf = False
        # for s in tqdm.tqdm(range(N)):
        for s in range(N):
            t, c, k = sketch.updategen()
            Rec, CList = sketch.update(c, k, t)
            if Rec:
                sketch.record(CList, tosaveRunHist)
            if sketch.t >= SuperInfty:
                break

        if ToSave:
            sketch.savehist(mode="extracted", tosaveRunHist=tosaveRunHist)
            MtgAlldf[r] = utl.myLogunpack(sketch.snapshotHistdf, "Mtg", samplx)
            regAAlldf[r] = utl.myLogunpack(sketch.snapshotHistdf, "regA", samplx)

        if SaveHist > 0:
            SaveHist -= 1
            sketch.savehist(mode="csv")
            #utl.myplot(Sketches, "Mtg", N, r, utl.getPlotTitle(m, None, N, r, Round), msamplerate=100)
            #utl.myplot(Sketches, "a", N, r, utl.getPlotTitle(m, None, N, r, Round), False, msamplerate=100)
            #utl.myplot(DeathSketches, "DeadNum", N, r, utl.getPlotTitle(m, None, N, r, Round), False, msamplerate=100)
        sketch.refresh()

    if ToSave:
        MtgAlldf.to_csv("results/"+utl.VersionStr+"/"+utl.RunStr+"_Mtg_"
                        +str(BitperCounter)+"bits_"+sketch.name+".csv")
        regAAlldf.to_csv("results/"+utl.VersionStr+"/"+utl.RunStr+"_regA_"
                        +str(BitperCounter)+"bits_"+sketch.name+".csv")
