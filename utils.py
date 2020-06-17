import numpy as np
import time
import pickle
import matplotlib.pyplot as plt

VersionStr = "T6"
Infty = 32
# to us, values above 32 is a state not possible to appear in LL simulation. in simulation not even 16
MaxChange = 16
# I believe there should not be more than 16 changes happening on one counter. in simulation not even 13.
# except for some special sketches


def getTimeString():
    return time.strftime(time.strftime("%m_%d_%H_%M_%S"))


def getCodebook(pSize):
    cdbkfile = 'codebooks/Codebook-' + str(pSize) + '.pkl'
    with open(cdbkfile, "rb") as file:
        gCodebook = pickle.load(file)
    return gCodebook


def unpack(pN, df, datname, inxmax):
    dat = np.zeros(pN)
    for inx in range(inxmax):
        d = df[datname][inx]
        mint = int(df["t"][inx])
        maxt = int(df["t"][inx+1]) if (inx < inxmax-1) else pN
        for pt in range(mint, maxt):
            dat[pt] = d
    return dat


def myplot(mSketches, datname, pN, pr, mtitle="", reference=True):
    x = np.arange(pN)
    if reference:
        plt.plot(x, x, color="black")
    for sketch in mSketches:
        datHist = unpack(pN, sketch.snapshotHistdf, datname, sketch.snapshotHist_inx)
        plt.plot(x, datHist, color=sketch.color, label=sketch.name)
    plt.legend(loc="upper left")
    plt.title(mtitle)
    plt.savefig("figs/"+VersionStr+"_"+datname+"_"+getTimeString()+"_("+str(pr) + ").png")
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
    return "m=%d, q=%d, N=%d, %d/%d round" % (gm, gq, gN, gr+1, gR)

