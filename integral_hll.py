import numpy as np
import tqdm


def j(s, m):
    split = np.float64(0.0001)
    sum = np.float64(0)
    for i in tqdm.tqdm(range(1000000)):
        u = i * split
        value = np.power(u, s, dtype=np.float64) * \
                np.power(np.log2((u+2)/(u+1), dtype=np.float64), m, dtype=np.float64) * \
                split
        sum += value
    return sum


def alpha(m):
    return 1/(m*j(0, m))


def beta1(m):
    return np.sqrt(m*(j(1, m)/(j(0, m) ** 2)-1))

