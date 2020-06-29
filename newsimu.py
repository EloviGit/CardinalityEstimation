# this program runs simulations for various sketches and the code is arranged nicely

import numpy as np
import pandas as pd
import tqdm
import utils as utl
import sketches as sk

MaxBit = 600  # T8
# Maxbit = 1200  # T9
BitperCounter = 2
m = int(MaxBit/BitperCounter)
N = 3000
SuperInfty = 1e7
Round = 1
Upbd = (2**BitperCounter) - 2
# Size = 511
# AcName = "ac393"
# AcNName = "ac511N"
# AdaFrac = 0.2

ToSave = False
SaveHistIni = 1

samplN = 1000
expsamplx = np.array(np.arange(samplN+1), dtype=np.float64)/samplN * 10
samplx = np.power(10, expsamplx)

qList = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0]

Sketches = [sk.CurtainPCSASketch(300, 2, 3000, 1.5, 3)]

# names = [sketch.name for sketch in Sketches]
# DeathSketches = [sketch for sketch in Sketches if hasattr(sketch, "DeadNum")]
# invRegAlldf = pd.DataFrame(np.array(np.zeros((samplN, len(names))), dtype=np.float64), columns=names)

for sketch in Sketches:
    SaveHist = SaveHistIni
    MtgAlldf = pd.DataFrame(np.array(np.zeros((samplN + 1, Round)), dtype=np.float64), columns=list(range(Round)))
    print("Currently running Sketch"+sketch.name)
    # for r in tqdm.tqdm(range(Round)):
    for r in range(Round):
        tosaveRunHist = (SaveHist > 0)
        SketchReachedSupInf = False
        for s in tqdm.tqdm(range(N)):
            t, c, k = sk.updategen(sketch)
            Rec, CList = sketch.update(c, k, t)
            if Rec:
                sketch.record(CList, tosaveRunHist)
            if sketch.t >= SuperInfty:
                break

        if ToSave:
            sketch.savehist(mode="extracted", tosaveRunHist=tosaveRunHist)
            MtgAlldf[r] = utl.myLogunpack(sketch.snapshotHistdf, "Mtg", samplx)
            #invRegAlldf[sketch.name] += utl.myLogunpack(sketch.snapshotHistdf, "t", samplx)/Round

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
        #invRegAlldf.to_csv("results/Congregated_invRegA_3bit_"+utl.getTimeString()+".csv")
