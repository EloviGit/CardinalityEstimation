from utils import *


# artifitial codebook are functions from triplets to triplets
def ac688(ptriple):
    # 689 states, one of them is inf, inf, inf, excluded when counting sizes
    # literally no death
    newtripl = [0, 0, 0]
    InfN = 0
    InfRang = [8, 8, 13]
    for l in range(3):
        if ptriple[l] <= -2:
            newtripl[l] = -2
        elif -1<=ptriple[l]<=2 and InfN == 0:
            newtripl[l] = ptriple[l]
        elif 3<=ptriple[l]<=4 and InfN == 0:
            newtripl[l] = 4
        elif 5<=ptriple[l]<=7 and InfN == 0:
            newtripl[l] = 7
        elif InfN != 0 and ptriple[l] < InfRang[InfN]:
            newtripl[l] = ptriple[l]
        elif ptriple[l] >= InfRang[InfN]:
            newtripl[l] = Infty
            InfN += 1
    changed = newtripl[0] == ptriple[0] and newtripl[1] == ptriple[1] and newtripl[2] == ptriple[2]
    return tuple(newtripl), changed


def ac631(ptriple):
    # 632 states, one of them is inf, inf, inf, excluded when counting sizes
    newtripl = [0, 0, 0]
    InfN = 0
    InfRang = [7, 7, 13]
    for l in range(3):
        if ptriple[l] <= -2:
            newtripl[l] = -2
        elif -1<=ptriple[l]<=2 and InfN == 0:
            newtripl[l] = ptriple[l]
        elif 3<=ptriple[l]<=4 and InfN == 0:
            newtripl[l] = 4
        elif 5<=ptriple[l]<=6 and InfN == 0:
            newtripl[l] = 6
        elif InfN != 0 and ptriple[l] < InfRang[InfN]:
            newtripl[l] = ptriple[l]
        elif ptriple[l] >= InfRang[InfN]:
            newtripl[l] = Infty
            InfN += 1
    changed = newtripl[0] == ptriple[0] and newtripl[1] == ptriple[1] and newtripl[2] == ptriple[2]
    return tuple(newtripl), changed


def ac568(ptriple):
    # 569 states, one of them is inf, inf, inf, excluded when counting sizes
    newtripl = [0, 0, 0]
    infN = 0
    CoDict0 = {-1:-1, 0:0, 1:1, 2:2, 3:3, 4:5, 5:5}
    CoDict1 = {-1:-1, 0:0, 1:1, 2:2, 3:3, 4:4, 5:6, 6:6}
    CoDict2 = {-1:-1, 0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8}
    for l in range(3):
        if ptriple[l] <= -2:
            newtripl[l] = -2
        elif -1<=ptriple[l]<=5:
            newtripl[l] = CoDict0[ptriple[l]]
        else:
            newtripl[l] = Infty
            infN += 1

    if infN == 1:
        for l in range(3):
            if ptriple[l] <= -2:
                newtripl[l] = -2
            elif -1 <= ptriple[l] <= 6:
                newtripl[l] = CoDict1[ptriple[l]]
            else:
                newtripl[l] = Infty
    elif infN == 2:
        for l in range(3):
            if ptriple[l] <= -2:
                newtripl[l] = -2
            elif -1 <= ptriple[l] <= 8:
                newtripl[l] = CoDict2[ptriple[l]]
            else:
                newtripl[l] = Infty

    changed = newtripl[0] == ptriple[0] and newtripl[1] == ptriple[1] and newtripl[2] == ptriple[2]
    return tuple(newtripl), changed


def ac393(ptriple):
    # 394 states, one of them is inf, inf, inf, excluded when counting sizes
    # (-2, -1, 0, 1, 2, 4)
    # 6*6*6 + 3*7*7+3*9+1
    newtripl = [0, 0, 0]
    infN = 0
    CoDict0 = {-1:-1, 0:0, 1:1, 2:2, 3:4, 4:4}
    CoDict1 = {-1:-1, 0:0, 1:1, 2:2, 3:4, 4:4, 5:6, 6:6}
    CoDict2 = {-1:-1, 0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7}
    for l in range(3):
        if ptriple[l] <= -2:
            newtripl[l] = -2
        elif -1<=ptriple[l]<=4:
            newtripl[l] = CoDict0[ptriple[l]]
        else:
            newtripl[l] = Infty
            infN += 1

    if infN == 1:
        for l in range(3):
            if ptriple[l] <= -2:
                newtripl[l] = -2
            elif -1 <= ptriple[l] <= 6:
                newtripl[l] = CoDict1[ptriple[l]]
            else:
                newtripl[l] = Infty
    elif infN == 2:
        for l in range(3):
            if ptriple[l] <= -2:
                newtripl[l] = -2
            elif -1 <= ptriple[l] <= 7:
                newtripl[l] = CoDict2[ptriple[l]]
            else:
                newtripl[l] = Infty

    changed = newtripl[0] == ptriple[0] and newtripl[1] == ptriple[1] and newtripl[2] == ptriple[2]
    return tuple(newtripl), changed
