import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import utils as utl

Ctnbit, Belowbit = 2, 2
datname = "Mtg"

# qs = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
#qs = [2.6, 2.7, 2.8, 2.91, 3.0, 3.1, 3.2]
#qs = [3.8, 3.9, 3.94, 4.0, 4.1, 4.2]
# names = ["AdaLazyCtnPCSA-"+str(q)+"-"+str((2**(Ctnbit-1))-0.5)+"-"+str(Belowbit) for q in qs]
names = ["AdaLazyCtnPCSA-2.91-1.5-1", "CtnSTUnifOffs-3.94-1.5", "Thrs-2.0-14"]

Round = 30000
AllDf1 = pd.read_csv("results/T18/V07141615_LastRatio_1e6_fast07_15_07_51_25.csv")

df2 = pd.read_csv("results/"+utl.VersionStr+"/V07151431_LastRatio_1e6_fast07_15_15_31_46.csv")

AllDf1[names[0]] = df2[names[0]]


# baselineq = (np.arange(65, 136)-100)/100 + 3.94
#valq = np.array([utl.AdaLazyCtnPCSA_VarMemProdThry(q, 2**(Ctnbit-1), Belowbit-1)/(1200) for q in list(baselineq)])
# valq = np.array([utl.AdaLazyCtnPCSA_VarMemProdThry(q, 2**(Ctnbit-1), 0) for q in list(baselineq)])
# plsq = 1 + np.sqrt(valq)
# mnsq = 1 - np.sqrt(valq)
# oneq = np.ones(valq.shape)

base = np.array(np.arange(100)/100) + 0.5
counter = np.zeros((3, 100), dtype=int)
rounds = [3000, 30000, 30000]

for j in range(3):
    for i in range(rounds[j]):
        x1 = int(AllDf1[names[j]][i] * 100 - 50)
        if x1 < 0:
            counter[j][0] += 1
        elif x1 >= 100:
            counter[j][99] += 1
        else:
            counter[j][x1] += 1

counter[0] *= 10
colors = ["red", "blue", "green"]
# samplN = 600 + 1
# expsamplx = np.array(np.arange(samplN), dtype=np.float64)/samplN * 6
# samplx = np.power(10, expsamplx)

for i in range(3):
    vec = counter[i]
    # retv = np.sum(np.square(vec-1))/Round
    #qList = [qs[i]]*len(vec)
    #plt.scatter(qList, vec, color="black", alpha=0.01, s=5)
    #plt.scatter(qList, np.square(vec-1)*(Ctnbit+Belowbit-1)*400, alpha=0.1, color="black", s=5)
    #plt.scatter(qs[i], np.average(np.square(vec-1))*1200, color="black")
    plt.plot(base, vec, color=colors[i], label=names[i])
#plt.plot(baselineq, valq, color="blue")
#plt.plot(baselineq, plsq, color="blue")
#plt.plot(baselineq, oneq, color="blue")
#plt.plot(baselineq, mnsq, color="blue")
#plt.title("Avg, RemArea*Lambda, at 1e6, %d ctn, %d board, ttl 1200bits, LazyCtnPCSA" % (Ctnbit, Belowbit - 1))
#plt.title("Mtg, VarMemProd, at 1e6, %d ctn, %d board, ttl 1200bits, LazyCtnPCSA" % (Ctnbit, Belowbit - 1))
plt.legend(loc="upper left")
plt.title("Mtg, Ratio, at 1e6, 1200bits, 30000 rounds")
#plt.title("RemArea*Lambda, at 1e6, %d ctn, %d below, ttl 1200bits, CtnPCSA" % (Ctnbit, Belowbit))
#plt.title("Mtg, VarMemProd, at 1e6, %d ctn, %d below, ttl 1200bits, CtnPCSA" % (Ctnbit, Belowbit - 1))
plt.savefig("figs/"+utl.VersionStr+"_"+datname+"_"+utl.getTimeString()+".png")
plt.show()



