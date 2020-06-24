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
SuperEpsilon = 1e-20
Round = 1000
Upbd = 6
Size = 511
AcName = "ac393"
AcNName = "ac511N"
AdaFrac = 0.2

PlotPeriod = 1
ToSave = True

Sketches = [
    sk.LLSketch(m, 2.0, N),
    sk.ThrsSketch(m, 1.414, N, pUpbd=Upbd),
    sk.ThrsSketch(m, 2.0, N, pUpbd=Upbd),
    sk.ThrsSketch(m, 4.0, N, pUpbd=Upbd),
    sk.ThrsSketch(m, 8.0, N, pUpbd=Upbd),
    sk.ThrsSketch(m, 16.0, N, pUpbd=Upbd),
    sk.ThrsSketch(m, 32.0, N, pUpbd=Upbd),
    #sk.Min2CdbkSketch(m, q, N, Size),
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

names = [sketch.name for sketch in Sketches]
DeathSketches = [sketch for sketch in Sketches if hasattr(sketch, "DeadNum")]

SketchesReachedSupInf = []

samplN = 1000
expsamplx = np.array(np.arange(samplN), dtype=np.float64)/samplN * 20
samplx = np.power(10, expsamplx)

MtgAlldf = pd.DataFrame(np.array(np.zeros((samplN, len(names))), dtype=np.float64),
                     columns=names)

invRegAlldf = pd.DataFrame(np.array(np.zeros((samplN, len(names))), dtype=np.float64),
                     columns=names)

for r in tqdm.tqdm(range(Round)):
    ToPlot = (r % PlotPeriod == 0)
    for s in range(N):
        for sketch in Sketches:
            if sketch not in SketchesReachedSupInf:
                t, c, k = sk.updategen(sketch)
                if ToSave:
                    Rec, CList = sketch.update(c, k, t)
                    if Rec:
                        sketch.record(CList)
                else:
                    sketch.update(c, k, t)
                if sketch.t >= SuperInfty:
                    SketchesReachedSupInf.append(sketch)
                if hasattr(sketch, "DeadNum") and sketch.DeadNum == sketch.m:
                    # all counters died out
                    SketchesReachedSupInf.append(sketch)
        if len(SketchesReachedSupInf) == len(Sketches):
            # all sketches has reached 1e20
            break

    if ToSave:
        for sketch in Sketches:
            sketch.savehist(mode="extracted", sr=r)
            MtgAlldf[sketch.name] += utl.myLogunpack(sketch.snapshotHistdf, "Mtg", samplx)/Round
            invRegAlldf[sketch.name] += utl.myLogunpack(sketch.snapshotHistdf, "t", samplx)/Round

    if ToSave and ToPlot:
        pass
        # for sketch in Sketches:
        #      sketch.savehist(mode="csv")
        # #utl.myplot(Sketches, "Mtg", N, r, utl.getPlotTitle(m, None, N, r, Round), msamplerate=100)
        #utl.myplot(Sketches, "a", N, r, utl.getPlotTitle(m, None, N, r, Round), False, msamplerate=100)
        #utl.myplot(DeathSketches, "DeadNum", N, r, utl.getPlotTitle(m, None, N, r, Round), False, msamplerate=100)

    for sketch in Sketches:
        sketch.refresh()
    SketchesReachedSupInf = []

MtgAlldf.to_csv("results/Congregated_Mtg_3bit_"+utl.getTimeString()+".csv")
invRegAlldf.to_csv("results/Congregated_invRegA_3bit_"+utl.getTimeString()+".csv")
