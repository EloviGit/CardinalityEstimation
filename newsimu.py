# this program runs simulations for various sketches and the code is arranged nicely

import numpy as np
import pandas as pd
import tqdm
import utils as utl
import sketches as sk
import sys

utl.mkdir()

#Curtainbit, Boardbit = 2, 1
Round = 25000
N = 1e6
OnlySaveLast = True
ToSave = False
SaveHistIni = 0

MaxBit = 1200
#BitperCounter = Curtainbit + Boardbit
#m = int(MaxBit/BitperCounter)
# Upbd = (2**BitperCounter) - 2
# Size = 511
# AcName = "ac393"
# AcNName = "ac511N"
# AdaFrac = 0.2
scale = 6
samplN = 100 * scale
expsamplx = np.array(np.arange(samplN+1), dtype=np.float64)/samplN * scale
samplx = np.power(10, expsamplx)


Sketches = [
            sk.DoubleCurtainSketch(300, 3.0, N, 1.5),
            sk.SecondHighCurtainSketch(300, 4.0, N, 1.5, 3),
            #sk.GroupCurtainPCSA(450, 4.0, N, 1.5, 2, pgroupSize=3)
            #sk.AdaLazyCtnPCSA_Ctn2bit_Board1bit_Sketch(400, 2.91, 1e6),
            #sk.CurtainSTUnifOffstSketch(1500, 3.94, N, 1.5),
            #sk.ThrsSketch(750, 2.0, N, 14),
            ]

MtgAlldf = pd.DataFrame([])
regAAlldf = pd.DataFrame([])
RatioAlldf = pd.DataFrame(np.zeros((Round, len(Sketches))), columns=[r_sketch.name for r_sketch in Sketches])
for sketch in Sketches:
    SaveHist = SaveHistIni
    if ToSave:
        MtgAlldf = pd.DataFrame(np.zeros((samplN+1, Round)), columns=list(range(Round)))
        regAAlldf = pd.DataFrame(np.zeros((samplN+1, Round)), columns=list(range(Round)))
    print("Currently running Sketch "+sketch.name)
    for r in tqdm.tqdm(range(Round)):
        tosaveRunHist = (SaveHist > 0)
        # for s in tqdm.tqdm(range(N)):
        while sketch.t < sketch.N:
            t, c, k = sketch.updategen()
            Rec, CList = sketch.update(c, k, t)
            if Rec and (not OnlySaveLast):
                sketch.record(CList, tosaveRunHist)

        if ToSave:
            sketch.savehist(mode="extracted", tosaveRunHist=tosaveRunHist)
            MtgAlldf[r] = utl.myLogunpack(sketch.snapshotHistdf, "Mtg", samplx)
            regAAlldf[r] = utl.myLogunpack(sketch.snapshotHistdf, "regA", samplx)

        if OnlySaveLast:
            RatioAlldf[sketch.name][r] = np.float64(sketch.Mtg/sketch.N)

        if SaveHist > 0:
            SaveHist -= 1
            sketch.savehist(mode="csv")

        sketch.refresh()

    if ToSave:
        MtgAlldf.to_csv("results/"+utl.VersionStr+"/"+utl.RunStr+"_Mtg_"+sketch.name+"_"+utl.getTimeString()+".csv")
        regAAlldf.to_csv("results/"+utl.VersionStr+"/"+utl.RunStr+"_regA_"+sketch.name+"_"+utl.getTimeString()+".csv")

if OnlySaveLast:
    RatioAlldf.to_csv("results/"+utl.VersionStr+"/"+utl.RunStr+"_LastRatio_1e6_"+utl.getTimeString()+".csv")

print([nsketch.name for nsketch in Sketches])
