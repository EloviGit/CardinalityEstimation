import pandas as pd
import numpy as np
import utils as utl



MtgRdf = pd.read_csv("results/Mtg_06_17_02_50_18.csv")
names = ["LL", "AdaThrs-7-0.2", "ArtifCdbkN-ac511N", "Crtn-4", "CtnEvnOfs-3.5"]

VarsDf = pd.DataFrame([[0, 0, 0, 0, 0]], columns=names, dtype=float)

for name in names:
    mtgs = np.array(MtgRdf[name])
    vars = np.sum(np.square(mtgs/100000-1))/1000
    VarsDf[name][0] = vars

VarsDf.to_csv("results/Congregated_"+utl.getTimeString()+".csv")
