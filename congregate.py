import pandas as pd
import numpy as np
import utils as utl
#import newsimu as ns
import tqdm


names = ["LL", "Thrs-1.414-14", "Thrs-2.0-14", "Thrs-4.0-14", "Thrs-8.0-14",
            "Thrs-16.0-14", "Thrs-32.0-14"]
colors = ["red", "green", "blue", "yellow", "m", "c", "orange"]

ncdfs = []

datname = "invRegA"
Round = 1000

samplN = 1000
expsamplx = np.array(np.arange(samplN), dtype=np.float64)/samplN * 20
samplx = np.power(10, expsamplx)


AllDf = pd.DataFrame(np.array(np.zeros((samplN, len(names))), dtype=np.float64),
                     columns=names)

for i in range(len(names)):
    name = names[i]
    color = colors[i]
    overalldf = np.zeros(samplN, dtype=np.float64)
    for r in tqdm.tqdm(range(Round)):
        newdf = pd.read_csv("TTLHist/T8_V1/shortHist_" + name + "(" + str(r) + ").csv")
        newdfPacked = utl.myLogunpack(newdf, datname, samplx)
        overalldf += newdfPacked/Round
    ncdfs.append(tuple((name, color, overalldf.copy())))
    AllDf[name] = overalldf
    print(i)

utl.myLogplot(ncdfs, datname, samplx, "using 4bits")

AllDf.to_csv("results/Congregated_"+datname+"_4bit_"+utl.getTimeString()+".csv")
