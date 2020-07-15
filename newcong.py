# this file congragetes the relative variances of different sketches to provide data for scatter graph
import pandas as pd
import numpy as np
import utils as utl
import tqdm


# qList = [2.6, 2.7, 2.8, 2.91, 3.0, 3.1, 3.2]
qList = [3.8, 3.9, 3.94, 4.0, 4.1, 4.2]

#names = ["AdaLazyCtnPCSA-"+str(q)+"-1.5-2" for q in qList]
names = ["CtnSTUnifOffs-"+str(q)+"-1.5" for q in qList]
#exnames = ["ex_CtnSTUnifOffs-"+str(q)+"-1.5" for q in qList]

datname = "Mtg"
Round = 600

samplN = 600
expsamplx = np.array(np.arange(samplN+1), dtype=np.float64)/samplN * 6
samplx = np.power(10, expsamplx)

base = np.array(np.arange(100)/100) + 0.5
counter = np.zeros(base.shape, dtype=int)

InsertionInx = 600 # 1e10
InsertionT = 1e6

AllDf = pd.DataFrame(np.array(np.zeros(5000), dtype=np.float64), columns=["0"])

#filenames = ["results/T9/V1811_Mtg_4bits_"+name+".csv" for name in names]
# filenames = ["results/T9/V2243_Mtg_2bits_"+name+".csv" for name in names]
# filenames = ["results/T9/V2243_Mtg_2bits_"+name+".csv" for name in names]
# filenames = ["results/T10/V271453_Mtg_2bits_"+name+".csv" for name in names]
# filenames = ["results/T11/V291944_Mtg_2bits_"+name+".csv" for name in names]
# filenames = ["results/T11/V302300_Mtg_4bits_"+name+".csv" for name in names]
# filenames = ["results/T11/V07010216_Mtg_2bits_"+name+".csv" for name in names]
#filenames = ["results/"+utl.VersionStr+"/"+utl.RunStr+"_"+datname+"_"+str(bitused)+"bits_"+name+".csv" for name in names]
# filenames = ["results/"+utl.VersionStr+"/"+utl.RunStr+"_"+datname+"_"+name+".csv" for name in names]
2#exfilenames = ["results/"+utl.VersionStr+"/"+utl.RunStr+"_"+datname+"_"+name+".csv" for name in exnames]
# filename = "cong/T16/Mtg_CtnSTUnifOffs_1.5_ratio_1e6_07_13_10_39_42.csv"
filename = "results/T17/V07131204_LastRatio_1000000.0_AdaLazyCtnPCSA-2.91-1.5-2.csv"

newdf = pd.read_csv(filename)
newdfn = np.array(newdf)
#exnewdf = pd.read_csv(exfilenames[i])
#exvalues = np.array(exnewdf.iloc[InsertionInx]/InsertionT, dtype=np.float64)
for i in range(5000):
    AllDf["0"][i] = newdfn[0][i+1]

AllDf.to_csv("cong/"+utl.VersionStr+"/"+datname+"_AdaLazyCtnPCSA_1.5_2_ratio_1e6_"+utl.getTimeString()+".csv")
#AllDf.to_csv("cong/"+utl.VersionStr+"/"+datname+"_CtnSTUnifOffs_1.5_ratio_1e6_"+utl.getTimeString()+".csv")
