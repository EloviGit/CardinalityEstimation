# this program runs simulations for various sketches and the code is arranged nicely

import numpy as np
import pandas as pd
import tqdm
import utils as utl
import sketches as sk
import sys

utl.mkdir()

#Curtainbit, Boardbit = 2, 1
Round = 3000
N = 20000
OnlySaveLast = True
ToSave = False
SaveHistIni = 0

MaxBit = 12000
#BitperCounter = Curtainbit + Boardbit
#m = int(MaxBit/BitperCounter)
SuperInfty = 1e6
# Upbd = (2**BitperCounter) - 2
# Size = 511
# AcName = "ac393"
# AcNName = "ac511N"
# AdaFrac = 0.2
samplN = 600
expsamplx = np.array(np.arange(samplN+1), dtype=np.float64)/samplN * 6
samplx = np.power(10, expsamplx)


Sketches = [
            sk.AdaLazyCtnPCSA_Ctn2bit_Board1bit_Sketch(400, 2.91, N, pverbos=1),
            #sk.CurtainSTUnifOffstSketch(600, 3.94, N, 1.5),
            #sk.ThrsSketch(300, 2.0, N, 14),
            ]

RatioAlldf = pd.DataFrame(np.zeros((Round, len(Sketches))), columns=[r_sketch.name for r_sketch in Sketches])
for sketch in Sketches:
    SaveHist = SaveHistIni
    if ToSave:
        MtgAlldf = pd.DataFrame(np.zeros((samplN+1, Round)), columns=list(range(Round)))
        regAAlldf = pd.DataFrame(np.zeros((samplN+1, Round)), columns=list(range(Round)))
    print("Currently running Sketch"+sketch.name)
    for r in tqdm.tqdm(range(Round)):
        tosaveRunHist = (SaveHist > 0)
        SketchReachedSupInf = False
        # for s in tqdm.tqdm(range(N)):
        for s in range(N):
            t, c, k = sketch.updategen()
            Rec, CList = sketch.update(c, k, t)
            if Rec and (not OnlySaveLast):
                sketch.record(CList, tosaveRunHist)
            if sketch.t >= SuperInfty:
                break

        if ToSave:
            sketch.savehist(mode="extracted", tosaveRunHist=tosaveRunHist)
            MtgAlldf[r] = utl.myLogunpack(sketch.snapshotHistdf, "Mtg", samplx)
            regAAlldf[r] = utl.myLogunpack(sketch.snapshotHistdf, "regA", samplx)

        if OnlySaveLast:
            RatioAlldf[sketch.name][r] = np.float64(sketch.Mtg/SuperInfty)

        if SaveHist > 0:
            SaveHist -= 1
            sketch.savehist(mode="csv")

        sketch.refresh()

    if ToSave:
        MtgAlldf.to_csv("results/"+utl.VersionStr+"/"+utl.RunStr+"_Mtg_"+sketch.name+"_"+utl.getTimeString()+".csv")
        regAAlldf.to_csv("results/"+utl.VersionStr+"/"+utl.RunStr+"_regA_"+sketch.name+"_"+utl.getTimeString()+".csv")

if OnlySaveLast:
    RatioAlldf.to_csv("results/"+utl.VersionStr+"/"+utl.RunStr+"_LastRatio_1e6_fast"+utl.getTimeString()+".csv")
