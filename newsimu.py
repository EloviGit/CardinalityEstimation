# this program runs simulations for various sketches and the code is arranged nicely

import numpy as np
import pandas as pd
import tqdm
import utils as utl
import sketches as sk
import samplers as spl
import sys

utl.mkdir()

Round = 30000
N = 1e6
scale = 6
SaveLast = True
SaveLog = False
SaveHist = False
# MaxBit = 1200

LogScaleSampleContents = ["Mtg"] if SaveLog else []
OnlyLastSampleContents = [["ten", "not"][tenstr]+str(i+tenstr) for tenstr in range(2) for i in range(4)] if SaveLast else []

Sketches = [
            #sk.LLSketch(200, 2.0, N),
            #sk.DoubleCurtainSketch(300, 3.0, N, 1.5),
            sk.SecondHighCurtain_distributionResearch_Sketch(300, 3.0, N, 1.5, 3, pverbos=1),
            #sk.GroupCurtainPCSA(450, 4.0, N, 1.5, 2, pgroupSize=3)
            #sk.AdaLazyCtnPCSA_Ctn2bit_Board1bit_Sketch(400, 2.91, 1e6),
            #sk.CurtainSTUnifOffstSketch(1500, 3.94, N, 1.5),
            #sk.ThrsSketch(750, 2.0, N, 14),
            ]


names = [nsketch.name for nsketch in Sketches]
onlyLastSampler = spl.OnlyLastSampler(names, OnlyLastSampleContents, "differences", Round)
for sketch in Sketches:
    LogScaleSamplers = [spl.LogScaleSampler(sketch.name, datname, Round, scale=scale) for datname in LogScaleSampleContents]
    print("Currently running Sketch "+sketch.name)
    for r in tqdm.tqdm(range(Round)):
        tosaveRunHist = (SaveHist > 0)
        # for s in tqdm.tqdm(range(N)):
        while sketch.t < sketch.N:
            t, c, k = sketch.updategen()
            Rec, CList = sketch.update(c, k, t)
            if Rec:
                sketch.record(CList, tosaveRunHist)

        for sampler in LogScaleSamplers:
            sampler.sample(sketch, r)

        onlyLastSampler.sample(sketch, r)

        if SaveHist and r == 0:
            sketch.savehist(mode="csv")

        sketch.refresh()

    for sampler in LogScaleSamplers:
        sampler.save()

onlyLastSampler.save()
print(names)
print(onlyLastSampler.sknames)

# abandoned parameters.
# BitperCounter = Curtainbit + Boardbit
# m = int(MaxBit/BitperCounter)
# Upbd = (2**BitperCounter) - 2
# Size = 511
# AcName = "ac393"
# AcNName = "ac511N"
# AdaFrac = 0.2
