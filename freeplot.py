import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import utils as utl


# names = ["Thrs-1.4-6", "Thrs-1.6-6", "Thrs-1.8-6", "Thrs-2.0-6", "Thrs-2.2-6",
#          "Thrs-2.4-6", "Thrs-2.6-6", "Thrs-2.8-6", "Thrs-3.0-6", "Thrs-3.2-6",
#          "Thrs-3.4-6", "Thrs-3.6-6", "Thrs-3.8-6", "Thrs-4.0-6"]

# names = ["Thrs-1.4-14", "Thrs-1.6-14", "Thrs-1.8-14", "Thrs-2.0-14", "Thrs-2.2-14",
#          "Thrs-2.4-14", "Thrs-2.6-14", "Thrs-2.8-14", "Thrs-3.0-14", "Thrs-3.2-14",
#          "Thrs-3.4-14", "Thrs-3.6-14", "Thrs-3.8-14", "Thrs-4.0-14"]

# names = ["CtnSawTeeth-1.5-1.5", "CtnSawTeeth-2.0-1.5", "CtnSawTeeth-3.0-1.5",
#          "CtnSawTeeth-4.0-1.5", "CtnSawTeeth-5.0-1.5", "CtnSawTeeth-6.0-1.5",
#          "CtnSawTeeth-7.0-1.5",
#          "CtnSTUnifOffs-8.0-1.5", "CtnSTUnifOffs-10.0-1.5", "CtnSTUnifOffs-12.0-1.5"]

names = ["CtnStar-1.5-6", "CtnStar-2.0-6", "CtnStar-2.5-6", "CtnStar-3.0-6",
         "CtnStar-3.5-6", "CtnStar-4.0-6", "CtnStar-4.5-6", "CtnStar-5.0-6",
         "CtnStar-5.5-6", "CtnStar-6.0-6", "CtnStar-7.0-6", "CtnStar-8.0-6",
         "CtnStar-9.0-6", "CtnStar-10.0-6", "CtnStar-12.0-6",
]

# qs = [1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6, 2.8, 3.0, 3.2, 3.4, 3.6, 3.8, 4.0]
# qs = [1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 12.0]
qs = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0]
#names = ["LL", "Thrs-1.414-14", "Thrs-2.0-14", "Thrs-4.0-14", "Thrs-8.0-14", "Thrs-16.0-14", "Thrs-32.0-14"]
#colors = ["red", "green", "blue", "yellow", "m", "c", "orange"]

Round = 1000
datname = "Mtg"

samplN = 1000
expsamplx = np.array(np.arange(samplN + 1), dtype=np.float64)/samplN * 20
samplx = np.power(10, expsamplx)

#AllDf = pd.read_csv("cong/"+utl.VersionStr+"/Mtg_3bit_relativeVar_1e15_06_24_17_40_35.csv") # graph of 3 bits, relative var at 1e15
#AllDf = pd.read_csv("cong/"+utl.VersionStr+"/Mtg_3bit_ratio_1e15_06_24_17_43_03.csv") # graph of 3 bits, relative var at 1e15
#AllDf = pd.read_csv("cong/"+utl.VersionStr+"/Mtg_3bit_ratio_1e10_06_24_19_26_07.csv") # graph of 3 bits, ratio at 1e10
#AllDf = pd.read_csv("cong/"+utl.VersionStr+"/Mtg_4bit_ratio_1e15_06_24_21_57_18.csv") # graph of 4 bits, ratio at 1e15
#AllDf = pd.read_csv("cong/"+utl.VersionStr+"/Mtg_2bit_ratio_1e15_06_25_16_34_45.csv") # graph of 2 bits, curtain, ratio at 1e15
# AllDf = pd.read_csv("cong/"+utl.VersionStr+"/Mtg_CtnStar_3bit_ratio_1e15_06_25_21_14_57.csv") # graph of 3 bits, curtainStar, ratio at 1e15
AllDf = pd.read_csv("cong/"+utl.VersionStr+"/Mtg_CtnStar_3bit_ratio_1e15_06_25_22_11_57.csv") # graph of 3 bits, curtainStar, revised, ratio at 1e15

# for i in range(len(names)):
#     name = names[i]
#     relativeVar = np.square(vec/samplx - 1)
#     plt.plot(expsamplx[250:], relativeVar[250:], label=name)
# plt.legend(loc="upper left")
# plt.title("Mtg, relative variance, from 1e5, log-scale, using 3 bits")
# plt.savefig("figs/"+utl.VersionStr+"_"+datname+"_"+utl.getTimeString()+".png")
# plt.show()

T = np.float64(1e15)

for i in range(3, len(names)):
    name = names[i]
    vec = AllDf[name]
    retv = np.sum(np.square(vec-1))/Round
    qList = [qs[i]]*len(vec)
    plt.scatter(qs[i], retv)
    # plt.scatter(qList, np.log10(vec))
# plt.title("Mtg, ratio, log10, at 1e15, using 3 bits, CurtainStar")
plt.title("Mtg, emprRltvVar, at 1e15, using 3 bits, CurtainStar")
plt.savefig("figs/"+utl.VersionStr+"_"+datname+"_"+utl.getTimeString()+".png")
plt.show()
