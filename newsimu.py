# this program runs simulations for various sketches and the code is arranged nicely

import numpy as np
import pandas as pd
import tqdm
import utils as utl
import sketches as sk

MaxBit = 600  # T8
# Maxbit = 1200  # T9
BitperCounter = 3
m = int(MaxBit/BitperCounter)
N = 10000
SuperInfty = 1e20
Round = 1000
Upbd = (2**BitperCounter) - 2
# Size = 511
# AcName = "ac393"
# AcNName = "ac511N"
# AdaFrac = 0.2

ToSave = True
SaveHistIni = 3

samplN = 1000
expsamplx = np.array(np.arange(samplN+1), dtype=np.float64)/samplN * 20
samplx = np.power(10, expsamplx)

Sketches = [
    # sk.CurtainStarSketch(m, 1.5, N, pUpbd=Upbd),z
    # sk.CurtainStarSketch(m, 2.0, N, pUpbd=Upbd),
    # sk.CurtainStarSketch(m, 2.5, N, pUpbd=Upbd),
    # sk.CurtainStarSketch(m, 3.0, N, pUpbd=Upbd),
    # sk.CurtainStarSketch(m, 3.5, N, pUpbd=Upbd),
    # sk.CurtainStarSketch(m, 4.0, N, pUpbd=Upbd),
    sk.CurtainStarSketch(m, 4.5, N, pUpbd=Upbd),
    # sk.CurtainStarSketch(m, 5.0, N, pUpbd=Upbd),
    # sk.CurtainStarSketch(m, 5.5, N, pUpbd=Upbd),
    # sk.CurtainStarSketch(m, 6.0, N, pUpbd=Upbd),
    # sk.CurtainSawTeethSketch(m, 1.5, N, pDiffbd=1.5),
    # sk.CurtainSawTeethSketch(m, 2.0, N, pDiffbd=1.5),
    # sk.CurtainSawTeethSketch(m, 3.0, N, pDiffbd=1.5),
    # sk.CurtainSawTeethSketch(m, 4.0, N, pDiffbd=1.5),
    # sk.CurtainSawTeethSketch(m, 5.0, N, pDiffbd=1.5),
    # sk.CurtainSawTeethSketch(m, 6.0, N, pDiffbd=1.5),
    # sk.CurtainSawTeethSketch(m, 7.0, N, pDiffbd=1.5),
    # sk.CurtainSTUnifOffstSketch(m, 8.0, N, pDiffbd=1.5),
    # sk.CurtainSTUnifOffstSketch(m, 10.0, N, pDiffbd=1.5),
    # sk.CurtainSTUnifOffstSketch(m, 12.0, N, pDiffbd=1.5),
    # sk.ThrsSketch(m, 1.8, N, pUpbd=Upbd),
    # sk.ThrsSketch(m, 2.0, N, pUpbd=Upbd),
    # sk.ThrsSketch(m, 2.2, N, pUpbd=Upbd),
    # sk.ThrsSketch(m, 2.4, N, pUpbd=Upbd),
    # sk.ThrsSketch(m, 2.6, N, pUpbd=Upbd),
    # sk.ThrsSketch(m, 2.8, N, pUpbd=Upbd),
    # sk.ThrsSketch(m, 3.0, N, pUpbd=Upbd),
    # sk.ThrsSketch(m, 3.2, N, pUpbd=Upbd),
    # sk.ThrsSketch(m, 3.4, N, pUpbd=Upbd),
    # sk.ThrsSketch(m, 3.6, N, pUpbd=Upbd),
    # sk.ThrsSketch(m, 3.8, N, pUpbd=Upbd),
    # sk.ThrsSketch(m, 4.0, N, pUpbd=Upbd),
    # sk.CurtainStarSketch(m, 2.0, N, pUpbd=Upbd),
    # sk.CurtainStarSketch(m, 4.0, N, pUpbd=Upbd),
    # sk.CurtainStarSketch(m, 8.0, N, pUpbd=Upbd),
    # sk.CurtainStarSketch(m, 16.0, N, pUpbd=Upbd),
    # sk.CurtainStarSketch(m, 32.0, N, pUpbd=Upbd),
    # #sk.Min2CdbkSketch(m, q, N, Size),
    #sk.ArtifCdbkSketch(m, q, N, AcName),
    #sk.ArtifCdbkNSketch(m, q, N, AcNName, pcolor="purple"),
    # sk.CurtainSTUnifOffstSketch(m, 4.0, N, 1.5, pcolor="c", pname="CtnSTUO-q-4"),
    # sk.CurtainSketch(m, 8.0, N, 1.5, pcolor="orange", pname="Ctn-q-4"),
    # sk.CurtainSketch(m, 12.0, N, 1.5, pcolor="purple", pname="Ctn-q-6"),
    # sk.AdaThrsSketch(m, 2.0, N, 6, "yellow", "AdaThrs-2", 0.2),
    # sk.AdaThrsSketch(m, 2.5, N, 6, "orange", "AdaThrs-2", 0.15),
    # sk.AdaThrsSketch(m, 3.0, N, 6, "c", "AdaThrs-2", 0.1),
    # sk.CurtainSawTeethSketch(m, 2.0, N, 3.5, pcolor="blue", pname="CtnST-q-2"),
    # sk.CurtainSawTeethSketch(m, 4.0, N, 3.5, pcolor="green", pname="CtnST-q-2.5"),
    # sk.CurtainSawTeethSketch(m, 6.0, N, 3.5, pcolor="m", pname="CtnST-q-3"),
]

# names = [sketch.name for sketch in Sketches]
# DeathSketches = [sketch for sketch in Sketches if hasattr(sketch, "DeadNum")]
# invRegAlldf = pd.DataFrame(np.array(np.zeros((samplN, len(names))), dtype=np.float64), columns=names)

for sketch in Sketches:
    SaveHist = SaveHistIni
    MtgAlldf = pd.DataFrame(np.array(np.zeros((samplN + 1, Round)), dtype=np.float64), columns=list(range(Round)))
    print("Currently running Sketch"+sketch.name)
    for r in tqdm.tqdm(range(Round)):
        SketchReachedSupInf = False
        for s in range(N):
            t, c, k = sk.updategen(sketch)
            Rec, CList = sketch.update(c, k, t)
            if Rec:
                sketch.record(CList)
            if sketch.t >= SuperInfty:
                break

        if ToSave:
            sketch.savehist(mode="extracted")
            MtgAlldf[r] = utl.myLogunpack(sketch.snapshotHistdf, "Mtg", samplx)
            #invRegAlldf[sketch.name] += utl.myLogunpack(sketch.snapshotHistdf, "t", samplx)/Round

        if ToSave and SaveHist > 0:
            SaveHist -= 1
            sketch.savehist(mode="csv")
            #utl.myplot(Sketches, "Mtg", N, r, utl.getPlotTitle(m, None, N, r, Round), msamplerate=100)
            #utl.myplot(Sketches, "a", N, r, utl.getPlotTitle(m, None, N, r, Round), False, msamplerate=100)
            #utl.myplot(DeathSketches, "DeadNum", N, r, utl.getPlotTitle(m, None, N, r, Round), False, msamplerate=100)
        sketch.refresh()

    if ToSave:
        MtgAlldf.to_csv("results/"+utl.VersionStr+"/"+utl.RunStr+"revised_Mtg_"
                        +str(BitperCounter)+"bits_"+sketch.name+".csv")
        #invRegAlldf.to_csv("results/Congregated_invRegA_3bit_"+utl.getTimeString()+".csv")
