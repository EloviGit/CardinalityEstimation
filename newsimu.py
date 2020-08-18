# this program runs simulations for various sketches and the code is arranged nicely

import numpy as np
import pandas as pd
import tqdm
import utils as utl
import sketches as sk
import samplers as spl
import sys

utl.mkdir()

Round = 30
SaveHist = False
# MaxBit = 1200
N = 10000

#sketch1 = sk.CurtainSTUnifOffstSketch(100, 3.94, np.power(2, 70, dtype=np.float64), 1.5)
#sketch1 = sk.Infty_ThrsSketch(40, 2.0, np.power(2, 70, dtype=np.float64), 30)
#sketch1 = sk.SuperCompression128Sketch(np.power(2, 40, dtype=np.float64), pverbos=1)
#sketch2 = sk.SuperCompression128_noUnifOffs_Sketch(np.power(2, 40, dtype=np.float64), pverbos=1)
#sketch1 = sk.AdaLazyCtnPCSA_Ctn2bit_Board1bit_Sketch(100, 2.91, np.power(2, 50, dtype=np.float64), pverbos=0)
#sketch1 = sk.RawHyperLogLogSketch(21, 2.0, N, pthrs=63)
#sketch2 = sk.LLSketch(21, 2.0, N)
#sketch3 = sk.SuperCompression128Sketch(N)
Sketches = [sk.AdaLazyCtnPCSA_Ctn2bit_Board1bit_Sketch(m, 2.91, N*m, pverbos=0)
            for m in (74, 106, 150, 212, 300, 424, 600, 849)]

names = [nsketch.name for nsketch in Sketches]
#onlyLastSampler1 = spl.OnlyLastSampler([sketch1.name], ["estimator"], "RawHLL", Round)
onlyLastSampler2 = spl.OnlyLastSampler(names, ["Mtg"], "CtnPCSA", Round)
#failureSampler = spl.FailureSampler([sketch1.name], "failed", "RawHLL")
#LogScaleSampler = [spl.LogScaleSampler(sketch.name, "truncMtg", Round, scale=40, split=10, base=2) for sketch in Sketches]
#logScaleSampler = spl.LogScaleSampler(sketch1.name, "truncMtg", Round, scale=40, split=10, base=2)
Samplers = [onlyLastSampler2]
for sketch in Sketches:
    print("Currently running Sketch "+sketch.name)
    for r in tqdm.tqdm(range(Round)):
        tosaveRunHist = (SaveHist > 0)

        # while sketch.t < sketch.N:
        #     t, c, k = sketch.updategen()
        #     Rec, CList = sketch.update(c, k, t)
        #     if Rec:
        #         sketch.record(CList, tosaveRunHist)

        t, c, k = sketch.updategen()
        while t < sketch.N:
            Rec, CList = sketch.update(c, k, t)
            if Rec:
                sketch.record(CList, tosaveRunHist)
            t, c, k = sketch.updategen()
        sketch.last()

        for sampler in Samplers:
            sampler.sample(sketch, r)

        if SaveHist and r == 0:
            sketch.savehist(mode="csv")

        sketch.refresh()

    for sampler in Samplers:
        sampler.save(True)

for sampler in Samplers:
    sampler.save()

print(names)

# abandoned parameters.
# BitperCounter = Curtainbit + Boardbit
# m = int(MaxBit/BitperCounter)
# Upbd = (2**BitperCounter) - 2
# Size = 511
# AcName = "ac393"
# AcNName = "ac511N"
# AdaFrac = 0.2
