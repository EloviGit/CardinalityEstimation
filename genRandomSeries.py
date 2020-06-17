# we do not need to call numpy.random every time
# we can do them at the first time before the program starts.
# would this bring speed up?

import numpy as np
import pandas as pd
import tqdm
from utils import getRandSeriesString

q = 2.0
m = 300
N = 100000
Round = 200

randomSeries = np.zeros((N, 2), dtype=int)
for r in tqdm.tqdm(range(Round)):
    for t in range(N):
        randomSeries[t][0] = np.random.randint(m)
        randomSeries[t][1] = np.random.geometric(1/q)

    randomSeriesDf = pd.DataFrame(randomSeries, columns=["c", "k"])
    randomSeriesDf.to_csv(getRandSeriesString(q, m, N, r))


