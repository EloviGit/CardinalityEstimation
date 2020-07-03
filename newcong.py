# this file congragetes the relative variances of different sketches to provide data for scatter graph
import pandas as pd
import numpy as np
import utils as utl
import tqdm


# names = ["Thrs-1.4-6", "Thrs-1.6-6", "Thrs-1.8-6", "Thrs-2.0-6", "Thrs-2.2-6",
#          "Thrs-2.4-6", "Thrs-2.6-6", "Thrs-2.8-6", "Thrs-3.0-6", "Thrs-3.2-6",
#          "Thrs-3.4-6", "Thrs-3.6-6", "Thrs-3.8-6", "Thrs-4.0-6"]

# names = ["Thrs-1.4-14", "Thrs-1.6-14", "Thrs-1.8-14", "Thrs-2.0-14", "Thrs-2.2-14",
#          "Thrs-2.4-14", "Thrs-2.6-14", "Thrs-2.8-14", "Thrs-3.0-14", "Thrs-3.2-14",
#          "Thrs-3.4-14", "Thrs-3.6-14", "Thrs-3.8-14", "Thrs-4.0-14"]

# names = ["CtnSawTeeth-1.5-1.5", "CtnSawTeeth-2.0-1.5", "CtnSawTeeth-2.5-1.5", "CtnSawTeeth-3.0-1.5",
#          "CtnSawTeeth-3.5-1.5",
#          "CtnSawTeeth-4.0-1.5", "CtnSawTeeth-5.0-1.5", "CtnSawTeeth-6.0-1.5",
#          "CtnSawTeeth-7.0-1.5",
#          "CtnSTUnifOffs-8.0-1.5", "CtnSTUnifOffs-10.0-1.5", "CtnSTUnifOffs-12.0-1.5"]

# names = ["CtnStar-1.5-6", "CtnStar-2.0-6", "CtnStar-2.5-6", "CtnStar-3.0-6",
#          "CtnStar-3.5-6", "CtnStar-4.0-6", "CtnStar-4.5-6", "CtnStar-5.0-6",
#          "CtnStar-5.5-6", "CtnStar-6.0-6", "CtnStar-7.0-6", "CtnStar-8.0-6",
#          "CtnStar-9.0-6", "CtnStar-10.0-6", "CtnStar-12.0-6",
# ]

# qList = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5, 12.0]
# qList = [2.0, 3.0, 4.0, 5.0, 6.0]
#qList = [3.7, 3.75, 3.8, 3.85, 3.9, 3.95, 4.0, 4.05, 4.1, 4.15, 4.2, 4.25, 4.3]
# qList = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0]
# qList = [2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5]
# qList = [4.0]
qList = [2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]

names = ["CtnPCSA-"+str(q)+"-3.5-2" for q in qList]

bitused = 5

datname = "Mtg"
Round = 500

samplN = 600
expsamplx = np.array(np.arange(samplN+1), dtype=np.float64)/samplN * 6
samplx = np.power(10, expsamplx)

InsertionInx = 600 # 1e10
InsertionT = 1e6

AllDf = pd.DataFrame(np.array(np.zeros((Round, len(names))), dtype=np.float64),
                     columns=names)

# filenames = ["results/T9/Congregated_Mtg_3bits_Thrs-1.4-6_06_24_15_09_51.csv",
#              "results/T9/Congregated_Mtg_3bits_Thrs-1.6-6_06_24_15_13_40.csv",
#              "results/T9/Congregated_Mtg_3bits_Thrs-1.8-6_06_24_15_19_17.csv",
#              "results/T9/Congregated_Mtg_3bits_Thrs-2.0-6_06_24_15_27_20.csv",
#              "results/T9/Congregated_Mtg_3bits_Thrs-2.2-6_06_24_15_38_08.csv",
#              "results/T9/Congregated_Mtg_3bits_Thrs-2.4-6_06_24_15_49_53.csv",
#              "results/T9/Congregated_Mtg_3bits_Thrs-2.6-6_06_24_16_03_07.csv",
#              "results/T9/Congregated_Mtg_3bits_Thrs-2.8-6_06_24_16_16_45.csv",
#              "results/T9/Congregated_Mtg_3bits_Thrs-3.0-6_06_24_16_29_47.csv",
#              "results/T9/Congregated_Mtg_3bits_Thrs-3.2-6_06_24_16_42_43.csv",
#              "results/T9/Congregated_Mtg_3bits_Thrs-3.4-6_06_24_16_55_23.csv",
#              "results/T9/Congregated_Mtg_3bits_Thrs-3.6-6_06_24_17_07_54.csv",
#              "results/T9/Congregated_Mtg_3bits_Thrs-3.8-6_06_24_17_20_14.csv",
#              "results/T9/Congregated_Mtg_3bits_Thrs-4.0-6_06_24_17_32_35.csv",
#              ]

#filenames = ["results/T9/V1811_Mtg_4bits_"+name+".csv" for name in names]
# filenames = ["results/T9/V2243_Mtg_2bits_"+name+".csv" for name in names]
# filenames = ["results/T9/V2243_Mtg_2bits_"+name+".csv" for name in names]
# filenames = ["results/T10/V271453_Mtg_2bits_"+name+".csv" for name in names]
# filenames = ["results/T11/V291944_Mtg_2bits_"+name+".csv" for name in names]
# filenames = ["results/T11/V302300_Mtg_4bits_"+name+".csv" for name in names]
# filenames = ["results/T11/V07010216_Mtg_2bits_"+name+".csv" for name in names]
filenames = ["results/"+utl.VersionStr+"/"+utl.RunStr+"_"+datname+"_"+str(bitused)+"bits_"+name+".csv" for name in names]


for i in range(len(names)):
    name = names[i]
    newdf = pd.read_csv(filenames[i])
    values = np.array(newdf.iloc[InsertionInx], dtype=np.float64)
    #relvar = np.square(values/1e15 - 1)
    ratio = values/InsertionT
    # ratio = values
    AllDf[name] = ratio[1:]

AllDf.to_csv("cong/"+utl.VersionStr+"/"+datname+"_CtnPCSA_3.5_4bit_ratio_1e6_"+utl.getTimeString()+".csv")
