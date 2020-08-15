# this program runs simulations for various sketches and the code is arranged nicely

import numpy as np
import pandas as pd
import tqdm
import utils as utl
import sketches as sk
import samplers as spl
import sys

utl.mkdir()

Round = 10000
SaveHist = False
# MaxBit = 1200

#sketch1 = sk.CurtainSTUnifOffstSketch(100, 3.94, np.power(2, 70, dtype=np.float64), 1.5)
#sketch1 = sk.Infty_ThrsSketch(40, 2.0, np.power(2, 70, dtype=np.float64), 30)
sketch1 = sk.SuperCompression134Sketch(1000000, pverbos=0)
#sketch1 = sk.AdaLazyCtnPCSA_Ctn2bit_Board1bit_Sketch(100, 2.91, np.power(2, 50, dtype=np.float64), pverbos=0)
Sketches = [sketch1]

names = [nsketch.name for nsketch in Sketches]
onlyLastSampler1 = spl.OnlyLastSampler([sketch1.name], ["Mtg", "truncMtg"], "SupComp134", Round)
#onlyLastSampler2 = spl.OnlyLastSampler(['AdaLazyCtnPCSA-400-2.91-1.5-1', 'CtnSTUnifOffsLL-600-3.94-1.5'], ["Mtg"], "CtnPCSA_and_LL", Round)
#failureSampler = spl.FailureSampler(names, "failed", "RawPCSA")
#LogScaleSampler = [spl.LogScaleSampler(sketch.name, "Mtg", Round, scale=70, split=10, base=2) for sketch in Sketches]
Samplers = [onlyLastSampler1]
for sketch in Sketches:
    print("Currently running Sketch "+sketch.name)
    for r in tqdm.tqdm(range(Round)):
        tosaveRunHist = (SaveHist > 0)
        # t, c, k = sketch.updategen()
        while sketch.t < sketch.N:
            t, c, k = sketch.updategen()
            Rec, CList = sketch.update(c, k, t)
            if Rec:
                sketch.record(CList, tosaveRunHist)
        #sketch.last()

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
