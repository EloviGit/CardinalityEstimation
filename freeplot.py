import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import utils as utl

Ctnbit, Belowbit = 2, 2
datname = "Mtg"

# qs = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
#qs = [2.6, 2.7, 2.8, 2.91, 3.0, 3.1, 3.2]
#qs = [3.8, 3.9, 3.94, 4.0, 4.1, 4.2]
#ms = np.array([50, 71, 100, 141, 200, 283, 400, 566, 800, 1131])
#logms = np.log2(ms/50)
names = ['AdaLazyCtnPCSA-2.91-1.5-1', 'DoubleCtn-300-3.0-1.5', 'SecondHighCtn-300-4.0-1.5-3']

Round = 25000
df1 = pd.read_csv("results/T21/V07201430_LastRatio_1e6_07_22_08_53_09.csv")
df2 = pd.read_csv("results/T19/V07151431_LastRatio_1e6_fast_m400_07_15_22_10_43.csv")
AllDf1 = pd.concat((df1, df2), axis=1)
#AllDf1 = df1

# baselineq = (np.arange(65, 136)-100)/100 + 3.94
# valq = np.array([utl.AdaLazyCtnPCSA_VarMemProdThry(q, 2**(Ctnbit-1), Belowbit-1)/(1200) for q in list(baselineq)])
# valq = np.array([utl.AdaLazyCtnPCSA_VarMemProdThry(q, 2**(Ctnbit-1), 0) for q in list(baselineq)])
# plsq = 1 + np.sqrt(valq)
# mnsq = 1 - np.sqrt(valq)
# oneq = np.ones(valq.shape)

M_splits = 50
M_range = 0.1
base = utl.pdf_base(splits=M_splits, p_range=M_range)
counter = np.zeros((len(names), M_splits), dtype=int)

for j in range(len(names)):
     counter[j] = utl.pdf_count(AllDf1[names[j]][:Round], splits=M_splits, p_range=M_range)

# colors = ["red", "blue", "green", "yellow"]
# samplN = 600 + 1
# expsamplx = np.array(np.arange(samplN), dtype=np.float64)/samplN * 6
# samplx = np.power(10, expsamplx)

#basem = np.arange(460)/100
#expm = np.power(2, basem) * 50
#varm = utl.AdaLazyCtnPCSA_VarMemProdThry(2.91, 2, 1)/(3*expm)

for i in range(len(names)):
    #vec = AllDf1[names[i]][:Round]
    #val = np.average(np.square(vec-1)) * 1200
    #plt.scatter(qList, vec, color="black", alpha=0.01, s=5)
    #plt.scatter(qs[i], np.average(np.square(vec-1))*1200, color="black")
    #plt.scatter([logms[i]]*len(vec), vec, color="black", alpha=0.01, s=5)
    #plt.scatter(i+1, val, label=names[i])
    #plt.scatter(np.log2(ms[i] / 50), val, color="black")
    plt.plot(base, counter[i], label=names[i])
#plt.plot(baselineq, valq, color="blue")
#plt.title("Avg, RemArea*Lambda, at 1e6, %d ctn, %d board, ttl 1200bits, LazyCtnPCSA" % (Ctnbit, Belowbit - 1))
plt.title("Mtg, VarMemProd, at 1e6, 1200bits, %d Rounds" % (Round))
plt.legend(loc="upper left")
#plt.plot([0, 1200], [utl.AdaLazyCtnPCSA_VarMemProdThry(2.91, 2, 1)]*2, color="black")
#plt.plot(expm, varm, color="black")
#plt.xticks(logms, ms)
#plt.title("Mtg, RatioVar, at 1e5*m, m counters, 10000 rounds")
plt.savefig("figs/"+utl.VersionStr+"_"+datname+"_"+utl.getTimeString()+".png")
plt.show()



