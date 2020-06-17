# this program runs simulations for various sketches and the code is arranged nicely

import numpy as np
import tqdm
import utils as utl
import sketches as sk

m = 300
q = 2.0
N = 100000
Round = 1
Upbd = 5
Size = 393
AcName = "ac393"
AdaFrac = 0.2
Codebook = utl.getCodebook(Size)

for r in tqdm.tqdm(range(Round)):
    aLLSketch = sk.LLSketch(m, q, N)
    aThrsSketch = sk.ThrsSketch(m, q, N, Upbd)
    aAdaThreSketch = sk.AdaThrsSketch(m, q, N, Upbd, pAdaFrac=AdaFrac)
    #aCdbkSketch = sk.CdbkSketch(m, q, N, Codebook)
    #aMin2CdbkSketch = sk.Min2CdbkSketch(m, q, N, Codebook)
    aArtifCdbkSketch = sk.ArtifCdbkSketch(m, q, N, AcName)
    aCrtnSketch = sk.CurtainSketch(m, q, N, 4)
    Sketches = [aLLSketch, aArtifCdbkSketch, aAdaThreSketch, aThrsSketch, aCrtnSketch]
    DeathSketches = [aArtifCdbkSketch, aAdaThreSketch, aThrsSketch]
    for t in range(N):
        c = np.random.randint(m)
        k = np.random.geometric(1/q)
        for sketch in Sketches:
            Rec, CList = sketch.update(c, k, t)
            if Rec:
                sketch.record(CList, t)

    for sketch in Sketches:
        sketch.savehist()

    title = "m=%d, q=%d, N=%d, %d/%d round" % (m, q, N, r, Round)
    utl.myplot(Sketches, "Mtg", N, r, title)
    utl.myplot(DeathSketches, "DeadNum", N, r, title, False)
