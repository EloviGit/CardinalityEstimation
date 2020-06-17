# this program runs simulations for various sketches and the code is arranged nicely

import numpy as np
import pandas as pd
import tqdm
import utils as utl
import sketches as sk

m = 150
q = 2.0
N = 100000
Round = 1000
Upbd = 7
Size = 511
AcName = "ac393"
AcNName = "ac511N"
AdaFrac = 0.2

PlotPeriod = 100
UseRandS = False

Sketches = [
    sk.LLSketch(m, q, N),
    #sk.ThrsSketch(m, q, N, Upbd),
    sk.AdaThrsSketch(m, q, N, Upbd, pAdaFrac=AdaFrac, pcolor="green"),
    #sk.CdbkSketch(m, q, N, Size),
    #sk.Min2CdbkSketch(m, q, N, Size),
    #sk.ArtifCdbkSketch(m, q, N, AcName),
    sk.ArtifCdbkNSketch(m, q, N, AcNName, pcolor="purple"),
    sk.CurtainSketch(m, q, N, 4, pcolor="blue"),
    sk.CurtainEvenOffsetSketch(m, q, N, 3.5, pcolor="orange"),
]
names = [sketch.name for sketch in Sketches]
# DeathSketches = [sketch if hasattr(sketch, "DeadNum") for sketch in Sketches]

MtgR = np.zeros((Round, len(Sketches)))

for r in tqdm.tqdm(range(Round)):
    #randS = pd.read_csv(utl.getRandSeriesString(q, m, N, r))
    #randSdf = pd.DataFrame(randS)
    for t in range(N):
        #c, k = randSdf["c"][t], randSdf["k"][t]
        c, k = np.random.randint(m), np.random.geometric(1 / q)
        for sketch in Sketches:
            if r % PlotPeriod == 0:
                Rec, CList = sketch.update(c, k, t)
                if Rec:
                    sketch.record(CList, t)
            else:
                sketch.update(c, k, t)

    if r % PlotPeriod == 0:
        for sketch in Sketches:
            sketch.savehist()
        utl.myplot(Sketches, "Mtg", N, r, utl.getPlotTitle(m, q, N, r, Round))
        #utl.myplot(DeathSketches, "DeadNum", N, r, utl.getPlotTitle(m, q, N, r, Round))

    MtgR[r] = np.array([sketch.Mtg for sketch in Sketches])

    for sketch in Sketches:
        sketch.refresh()

MtgRdf = pd.DataFrame(MtgR, columns=names)
MtgRdf.to_csv("results/Mtg_"+utl.getTimeString()+".csv")

