import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import utils as utl


#names = ["LL", "Thrs-1.414-6", "Thrs-2.0-6", "Thrs-4.0-6", "Thrs-8.0-6","Thrs-16.0-6", "Thrs-32.0-6"]
names = ["LL", "Thrs-1.414-14", "Thrs-2.0-14", "Thrs-4.0-14", "Thrs-8.0-14", "Thrs-16.0-14", "Thrs-32.0-14"]

colors = ["red", "green", "blue", "yellow", "m", "c", "orange"]

datname = "Mtg"

samplN = 1000
expsamplx = np.array(np.arange(samplN), dtype=np.float64)/samplN * 20
samplx = np.power(10, expsamplx)

AllDf = pd.read_csv("results/Congregated_Mtg_4bit_06_23_22_46_39.csv") # graph of 4 bits, Mtg
#AllDf = pd.read_csv("results/Congregated_invRegA_4bit_06_23_23_11_37.csv") # graph of 4 bits, invRegA
#AllDf = pd.read_csv("results/Congregated_Mtg_3bit_06_23_23_41_17.csv") # graph of 3 bits, Mtg

for i in range(len(names)):
    name = names[i]
    color = colors[i]
    vec = AllDf[name]
    #relativeVar = np.square(vec/samplx - 1)
    plt.plot(samplx, vec, color=color, label=name)
plt.legend(loc="upper left")
plt.title("Mtg, using 4 bits")
plt.savefig("figs/"+utl.VersionStr+"_"+datname+"_"+utl.getTimeString()+".png")
plt.show()
