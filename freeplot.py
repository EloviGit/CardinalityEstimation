import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import utils as utl
import sys

# Ctnbit, Belowbit = 2, 2
datname = "truncMtg"

name = "SupComp134-39-2.91-1.5-1_truncMtg"

Round = 10000
df1 = pd.read_csv("results/T26/V08151554_OnlyLast_SupComp134_08_15_16_17_32.csv")

# baselineq = (np.arange(65, 136)-100)/100 + 3.94
# valq = np.array([utl.AdaLazyCtnPCSA_VarMemProdThry(q, 2**(Ctnbit-1), Belowbit-1)/(1200) for q in list(baselineq)])
# valq = np.array([utl.AdaLazyCtnPCSA_VarMemProdThry(q, 2**(Ctnbit-1), 0) for q in list(baselineq)])
# plsq = 1 + np.sqrt(valq)
# mnsq = 1 - np.sqrt(valq)
# oneq = np.ones(valq.shape)

M_splits = 50
M_range = 0.4
M_center = 1
base = utl.pdf_base(splits=M_splits, p_range=M_range, center=M_center)
counter = utl.pdf_count(df1[name][:Round]/np.power(2, 40, dtype=np.float64), splits=M_splits, p_range=M_range, center=M_center)

#sampvec = utl.exp_vector(70, 10, 2)
#plotsampvec = np.log2(sampvec)
#var1 = np.average(np.square(df1/sampvec.reshape((701, 1))-1), axis=1)



for i in range(1):
    # vec = AllDf1[names[i]+datnames[0]][:Round]/1e6
    # space = np.average(AllDf1[names[i] + datnames[2]][:Round]) if i <= 1 else 1200
    # val = np.average(np.square(vec - 1))
    # plt.scatter(i+1, val*space, label=names[i])
    #plt.scatter(qList, vec, color="black", alpha=0.01, s=5)
    #plt.scatter(qs[i], np.average(np.square(vec-1))*1200, color="black")
    #plt.scatter([logms[i]]*len(vec), vec, color="black", alpha=0.01, s=5)
    # plt.scatter(np.log2(df1[name]), counter, color="black")
    plt.plot(base, counter/100)
#plt.scatter(5, var4*1200, label=name4[0])
#plt.plot(baselineq, valq, color="blue")
# plt.scatter(1, 1200, alpha=0)
#plt.title("Avg, RemArea*Lambda, at 1e6, %d ctn, %d board, ttl 1200bits, LazyCtnPCSA" % (Ctnbit, Belowbit - 1))
plt.title("SuperCompresion-134, Distribution(%%), %d Rounds" % (Round))
#plt.legend(loc="upper left")
#plt.plot([0, 1200], [utl.AdaLazyCtnPCSA_VarMemProdThry(2.91, 2, 1)]*2, color="black")
#plt.plot(expm, varm, color="black")
#plt.xticks(logms, ms)
#plt.title("Mtg, RatioVar, at 1e5*m, m counters, 10000 rounds")
plt.savefig("figs/"+utl.VersionStr+"_"+datname+"_"+utl.getTimeString()+".png")
plt.show()



