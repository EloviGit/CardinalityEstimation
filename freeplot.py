import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import utils as utl

Ctnbit, Belowbit = 2, 1
datname = "Mtg"

qs = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]
names = ["CtnPCSA-"+str(q)+"-"+str((2**(Ctnbit-1))-0.5)+"-"+str(Belowbit) for q in qs]
Round = 500

AllDf = pd.DataFrame([])
if datname == "regA":
    if Ctnbit == 2 and Belowbit == 1:
        AllDf = pd.read_csv("cong/"+utl.VersionStr+"/regA_CtnPCSA_1.5_3bit_ratio_1e6_07_03_10_20_36.csv")
    elif Ctnbit == 2 and Belowbit == 2:
        AllDf = pd.read_csv("cong/"+utl.VersionStr+"/regA_CtnPCSA_1.5_4bit_ratio_1e6_07_03_10_18_30.csv")
    elif Ctnbit == 3 and Belowbit == 1:
        AllDf = pd.read_csv("cong/"+utl.VersionStr+"/regA_CtnPCSA_3.5_4bit_ratio_1e6_07_03_10_23_09.csv")
    elif Ctnbit == 3 and Belowbit == 2:
        AllDf = pd.read_csv("cong/"+utl.VersionStr+"/regA_CtnPCSA_3.5_5bit_ratio_1e6_07_03_10_23_35.csv")
elif datname == "Mtg":
    if Ctnbit == 2 and Belowbit == 1:
        AllDf = pd.read_csv("cong/"+utl.VersionStr+"/Mtg_CtnPCSA_1.5_3bit_ratio_1e6_07_03_10_20_56.csv")
    elif Ctnbit == 2 and Belowbit == 2:
        AllDf = pd.read_csv("cong/"+utl.VersionStr+"/Mtg_CtnPCSA_1.5_4bit_ratio_1e6_07_03_10_17_31.csv")
    elif Ctnbit == 3 and Belowbit == 1:
        AllDf = pd.read_csv("cong/"+utl.VersionStr+"/Mtg_CtnPCSA_3.5_4bit_ratio_1e6_07_03_10_21_53.csv")
    elif Ctnbit == 3 and Belowbit == 2:
        AllDf = pd.read_csv("cong/"+utl.VersionStr+"/Mtg_CtnPCSA_3.5_5bit_ratio_1e6_07_03_10_23_53.csv")

# baselineq = (np.arange(70, 131)-100)/100+4
# valq = np.array([(q/(q-1)*np.log(q)*(1+2/(np.power(q, 2-0.5)-1))*np.log2(2*2)/2) for q in list(baselineq)])

for i in range(len(names)):
    name = names[i]
    vec = AllDf[name]
    #retv = np.sum(np.square(vec-1))/Round
    qList = [qs[i]]*len(vec)
    plt.scatter(qs[i], np.average(np.square(vec-1))*1200)
    #plt.scatter(qs[i], np.average(vec) * 1e6)
    #plt.scatter(qList, vec*1e6, alpha=0.1, color="black", s=5)
#plt.plot(baselineq, valq)
#plt.title("Avg, RemArea*Lambda, at 1e6, %d ctn, %d below, ttl 1200bits, CtnPCSA" % (Ctnbit, Belowbit))
#plt.title("RemArea*Lambda, at 1e6, %d ctn, %d below, ttl 1200bits, CtnPCSA" % (Ctnbit, Belowbit))
plt.title("Mtg, VarMemProd, at 1e6, %d ctn, %d below, ttl 1200bits, CtnPCSA" % (Ctnbit, Belowbit))
plt.savefig("figs/"+utl.VersionStr+"_"+datname+"_"+utl.getTimeString()+".png")
plt.show()
