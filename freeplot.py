import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import utils as utl
import seaborn as sns
import tqdm
import sys

# Ctnbit, Belowbit = 2, 2
datnames = ["LL-200-2.0_Mtg", "RawHLL-200-2.0_estimator", "AdaLazyCtnPCSA-400-2.91-1.5-1_Mtg"]
datname="Mtg"

Round = 100000
df1 = pd.read_csv("results/T26/V08151554_OnlyLast_MtgHLL_08_16_22_42_22.csv")
df2 = pd.read_csv("results/T26/V08151554_OnlyLast_RawHLL_08_16_22_42_22.csv")
df3 = pd.read_csv("results/T26/V08151554_OnlyLast_MtgHLL_08_16_21_44_07.csv")
df4 = pd.read_csv("results/T26/V08151554_OnlyLast_RawHLL_08_16_21_44_07.csv")
df5 = pd.read_csv("results/T24/V07301627_OnlyLast_CtnPCSA_and_LL_07_30_16_50_36.csv")
df6 = pd.read_csv("results/T26/V08151554_OnlyLast_RawHLL_08_17_01_03_03.csv")
df7 = pd.read_csv("results/T26/V08151554_OnlyLast_MtgLLandPCSA_08_17_01_03_03.csv")
df8 = pd.read_csv("results/T26/V08151554_OnlyLast_RawHLL_08_17_02_03_21.csv")
df9 = pd.read_csv("results/T26/V08151554_OnlyLast_MtgLLandPCSA_08_17_02_03_21.csv")
MtgHLL = np.hstack((df1.__array__()[:, 1], df3.__array__()[:, 1], df7.__array__()[:, 1], df9.__array__()[:, 1]))
RawHLL = np.hstack((df2.__array__()[:, 1], df4.__array__()[:, 1], df6.__array__()[:, 1], df8.__array__()[:, 1]))
Curtain = np.hstack((df5.__array__()[:, 1], df7.__array__()[:, 2], df9.__array__()[:, 2]))
# df10 = pd.read_csv("results/T26/V08151554_OnlyLast_RawHLL_08_17_17_32_40.csv")
# df11 = pd.read_csv("results/T26/V08151554_OnlyLast_MtgLLandSupComp_08_17_17_32_40.csv")
# MtgHLL = df11.__array__()[:, 1]
# RawHLL = df10.__array__()[:, 1] # 0.6796; 0.6861
# Curtain = df11.__array__()[:, 2]
datas = [RawHLL, MtgHLL, Curtain]

# baselineq = (np.arange(65, 136)-100)/100 + 3.94
# valq = np.array([utl.AdaLazyCtnPCSA_VarMemProdThry(q, 2**(Ctnbit-1), Belowbit-1)/(1200) for q in list(baselineq)])
# valq = np.array([utl.AdaLazyCtnPCSA_VarMemProdThry(q, 2**(Ctnbit-1), 0) for q in list(baselineq)])
# plsq = 1 + np.sqrt(valq)
# mnsq = 1 - np.sqrt(valq)
# oneq = np.ones(valq.shape)

M_splits = 50
M_range = 0.2
M_center = 1
base = utl.pdf_base(splits=M_splits, p_range=M_range, center=M_center)
counter = np.zeros((3, M_splits))
for i in range(3):
    counter[i] = utl.pdf_count(datas[i]/1000000, splits=M_splits, p_range=M_range, center=M_center)

# sampvec = utl.exp_vector(40, 10, 2)
# plotsampvec = np.log2(sampvec)
# var1 = np.average(np.square(df1/sampvec.reshape((401, 1))-1), axis=1)
# var2 = np.average(np.square(df2/sampvec.reshape((401, 1))-1), axis=1)
#bias1 = np.average(df1/sampvec.reshape((401, 1)), axis=1)
# vars = [var1, var2]
names = ["HyperLogLog", "Martingale LogLog", "Martingale Curtain"]
colors = ["red", "green", "blue"]


for i in range(3):
    # vec = AllDf1[names[i]+datnames[0]][:Round]/1e6
    # space = np.average(AllDf1[names[i] + datnames[2]][:Round]) if i <= 1 else 1200
    # val = np.average(np.square(vec - 1))
    # plt.scatter(i+1, val*space, label=names[i])
    #plt.scatter(qList, vec, color="black", alpha=0.01, s=5)
    #plt.scatter(qs[i], np.average(np.square(vec-1))*1200, color="black")
    #plt.scatter([logms[i]]*len(vec), vec, color="black", alpha=0.01, s=5)
    # plt.scatter(np.log2(df1[name]), counter, color="black")
    # plt.scatter([plotsampvec[i]] * 100000, np.log2(alldata[i])-plotsampvec[i], color='black', alpha=0.0001)
    # plt.plot(plotsampvec[60:], vars[i][60:], label=names[i])
    #plt.hist(datas[i], bins=50, range=(1000000*(M_center-M_range), 1000000*(M_center+M_range)), density=True, label=names[i], alpha=0.5, color=colors[i])
    plt.plot(base+M_range/M_splits, counter[i], label=names[i], color=colors[i])
    plt.hist(datas[i]/1000000, bins=M_splits, range=(M_center - M_range, M_center + M_range), alpha=0.3, color=colors[i])
    #sns.distplot(datas[i], label=names[i], color=colors[i])
#plt.scatter(5, var4*1200, label=name4[0])
#plt.plot(baselineq, valq, color="blue")
# plt.scatter(1, 1200, alpha=0)
plt.xlabel("Ratio(Estimator/"+r"$10^6$"+")")
plt.ylabel("Counts")
plt.vlines(1, 0, 7900, alpha=0.5, colors="black")
plt.xlim((M_center-M_range, M_center+M_range))
plt.ylim((0, 7900))
#plt.title("Avg, RemArea*Lambda, at 1e6, %d ctn, %d board, ttl 1200bits, LazyCtnPCSA" % (Ctnbit, Belowbit - 1))
#plt.title("Mtg, count, at 1e6, 1200bits, %d rounds" % Round)
#plt.title("SuperCompresion-128, relativeVar, logscale, %d Rounds" % (Round))
#plt.title("SuperCompresion-134, scatterPlot, logscale, %d Rounds" % (Round))
plt.legend(loc="upper left")
plt.grid()
#plt.plot([0, 1200], [utl.AdaLazyCtnPCSA_VarMemProdThry(2.91, 2, 1)]*2, color="black")
#plt.plot(expm, varm, color="black")
#plt.xticks(logms, ms)
#plt.title("1200 bits, simulated 100,000 rounds for cardinality " + r"$10^6$")
plt.savefig("figs/"+utl.VersionStr+"_"+datname+"_"+utl.getTimeString()+".png")
plt.show()
