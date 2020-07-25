import numpy as np
import time
import pickle
import matplotlib.pyplot as plt
import math
import os

VersionStr = "T22"
RunStr = "V07242348"
Infty = 1000
MaxChange = 1000


def getTimeString():
    return time.strftime(time.strftime("%m_%d_%H_%M_%S"))


def getCodebook(pSize):
    cdbkfile = 'codebooks/Codebook-' + str(pSize) + '.pkl'
    with open(cdbkfile, "rb") as file:
        gCodebook = pickle.load(file)
    return gCodebook


def unpack(pN, df, datname, inxmax, samplerate):
    dat = np.zeros(int(pN/samplerate))
    for inx in range(inxmax):
        d = df[datname][inx]
        mint = int(df["t"][inx])
        maxt = int(df["t"][inx+1]) if (inx < inxmax-1) else pN
        for pt in range(mint, maxt):
            if pt % samplerate == 0:
                dat[int(pt/samplerate)] = d
    if datname == "a":
        dat = dat/300
    return dat


def myplot(mSketches, datname, pN, pr, mtitle="", reference=True, msamplerate=1):
    x = np.arange(int(pN/msamplerate)) * msamplerate
    if reference:
        plt.plot(x, x, color="black")
    for sketch in mSketches:
        datHist = unpack(pN, sketch.snapshotHistdf, datname, sketch.snapshotHist_inx, msamplerate)
        plt.plot(x, datHist, color=sketch.color, label=sketch.name)
    plt.legend(loc="upper left")
    plt.title(mtitle)
    plt.savefig("figs/"+VersionStr+"_"+datname+"_"+getTimeString()+"_("+str(pr) + ").png")
    plt.show()


def myLogunpack(df, datname, sampl):
    # sorry, but this function is abandoned.
    # df has two columns, t and Mtg
    # inxes give a list of possible t values.
    # if for inxes[m], it is between df[i] and df[i+1], then its value is df[i]
    # then we provide a packed dat
    samLen = len(sampl)
    dfLen = len(df["t"])
    inx_df = np.int64(0)
    inx_sam = np.int64(0)
    dat = np.zeros(samLen, dtype=np.float64)
    while inx_df < dfLen:
        maxT = np.float64(df["t"][inx_df + 1] if inx_df < dfLen - 1 else 1e100)
        while inx_sam < samLen and sampl[inx_sam] < maxT:
            dat[inx_sam] = df[datname][inx_df]
            inx_sam += 1
        inx_df += 1
    return dat


def uncoupled_Logunpack(val, time, sampl):
    # the first vector is the data to be sampled
    # the second vector is the time
    # if sampl[j] is between time[i] and time[i+1], dat[j]=val[i]
    # time[-1] = -infty, time[len]=+infty
    samLen = len(sampl)
    valLen = len(time)
    inx_val = np.int64(0)
    inx_sam = np.int64(0)
    dat = np.zeros(samLen, dtype=np.float64)
    while inx_val < valLen:
        maxT = np.float64(time[inx_val + 1] if inx_val < valLen - 1 else 1e100)
        while inx_sam < samLen and sampl[inx_sam] < maxT:
            dat[inx_sam] = val[inx_val]
            inx_sam += 1
        inx_val += 1
    return dat


def myLogplot(ncVecs, datname, samplx, mtitle):
    for ncVec in ncVecs:
        name, color, vec = ncVec
        plt.plot(samplx, vec, color=color, label=name)
    plt.legend(loc="upper left")
    plt.title(mtitle)
    plt.savefig("figs/"+VersionStr+"_"+datname+"_"+getTimeString()+".png")
    plt.show()


def TtoN(i, j, k, Range, Shift=0):
    # tuple to number
    return (i+Shift)*Range*Range + (j+Shift)*Range + (k+Shift)


def NtoT(s, Range, Shift=0):
    # number to tuple
    Square = Range*Range
    return int(s/Square) - Shift, ((int(s/Range)) % Range) - Shift, (s % Range) - Shift


def getRandSeriesString(gq, gm, gN, gr):
    return "RandomSeries/randSeries_%.1f_%06d_%06d_%06d.csv" % (gq, gm, gN, gr)


def getPlotTitle(gm, gq, gN, gr, gR):
    if gq is None:
        return "m=%d, N=%d, %d/%d round" % (gm, gN, gr+1, gR)
    else:
        return "m=%d, q=%d, N=%d, %d/%d round" % (gm, gq, gN, gr+1, gR)


def AdaLazyCtnPCSA_VarMemProdThry(q, a, h):
    return math.log(q) * (2 / (q ** (a - 0.5) - 1) + (1 / q) + q ** h - q ** (h - 1)) / (2 * ((q ** h) - (q ** (h - 1)))) * (math.log2(2 * a) + h)


def GroupCtnPCSA_VarMemProdThry(q, a, h, g):
    return math.log(q) * (g * (2 / (q ** (a - 0.5) - 1) + 1) + q ** h - q ** (h - 1)) / (2 * ((q ** h) - (q ** (h - 1)))) * (math.log2(2 * a)/g + h)


def CtnSTUnifOffs_VarMrnProfThry(q, a):
    return AdaLazyCtnPCSA_VarMemProdThry(q, a, 0)


def mkdir(path=VersionStr):
    rootpath = "D:\\PYTHON\\myPythonPrograms\\CardinalityEstimation\\"
    filepath = ["results\\", "cong\\", "TTLHist\\", "figs\\"]
    created = True
    for f_path in filepath:
        m_path = rootpath + f_path + path
        if not os.path.exists(m_path):
            os.makedirs(m_path)
            created = False
    if created:
        print("New version directories created.")
    return created


def pdf_count(data, splits=100, p_range=0.5, center=1.0):
    counter_a = np.zeros(splits, dtype=int)
    for i in range(len(data)):
        x1 = int((data[i]-center)*splits/(2*p_range) + splits/2)
        if 0 <= x1 < splits:
            counter_a[x1] += 1
    return counter_a


def pdf_base(splits=100, p_range=0.5, center=1.0):
    return (np.arange(splits)/splits-0.5)*(2*p_range)+center


def exp_vector(scale=6, split=100, base=10):
    # returns the vector of [b^0, b^{1/split}, b^{2/split}, ..., b^{scale}, b=base]
    return np.power(base, np.arange(scale*split+1)/split)
