# this program tunes parameters of variance memory product given by utils.py

import numpy as np
import utils as utl

qlist = np.arange(10000)/50000 + 3.7
# alist = [1, 2, 4, 8]
# hlist = [1, 2, 3, 4]
# glist = [1, 2, 3, 4]
# res = np.zeros((len(qlist), len(alist), len(hlist), len(glist)), dtype=np.float64)
res = np.zeros((len(qlist)), dtype=np.float64)
for q in range(len(qlist)):
    # for a in range(len(alist)):
    #     for h in range(len(hlist)):
    #         for g in range(len(glist)):
    #             res[q, a, h, g] = utl.GroupCtnPCSA_VarMemProdThry(qlist[q], alist[a], hlist[h], glist[g])
    res[q] = utl.GroupCtnPCSA_VarMemProdThry(qlist[q], 2, 2, 3)

# hes = res.reshape((res.size))
b = res.argsort()
print(b[:5])
print(qlist[b[:5]])
print(res[b[:5]])

