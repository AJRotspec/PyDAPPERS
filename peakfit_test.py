# -*- coding: utf-8 -*-
"""
Created on Wed Dec 10 13:42:09 2025

@author: Aaron2
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from numpy.polynomial.polynomial import Polynomial as P

def polyfit(x, y, deg = 2, graphing = False):
    # plt.plot(x[1:-1], np.diff(y, 2))
    xoffset = np.mean(x)
    x -= xoffset
    pol, fitdat = P.fit(x, y, deg, full = True)
    der = pol.deriv()
    curv = der.deriv()
    zeros = np.array([np.real(zer) for zer in der.roots() if np.imag(zer) == 0])
    peaks = np.array([zer for zer in zeros if curv(zer) < 0 and zer > x[0] and zer < x[-1]])
    if graphing:
        xfine = np.arange(x[0], x[-1], 2e-3)
        plt.plot(xfine + xoffset, pol(xfine), color = 'r')
        plt.vlines(peaks + xoffset, 0, pol(peaks), color = 'r')
    return peaks + xoffset
    
    
    # return np.array([zer for zer in zeros if curv(zer) > 0])
 
def partition(arr, gap = 1):
    ranges = []
    currlist = []
    for a1, a2 in zip(arr, arr[1:]):
        currlist.append(a1)
        if a1 < a2 - gap:
            ranges.append(currlist)
            currlist = []
    currlist.append(a2)
    ranges.append(currlist)
    return ranges

    
def difffit(x, y, graphing = False):
    toret = []
    dx = x[1] - x[0]
    xoffset = np.mean(x)
    # plt.plot(x[1:], np.diff(y))
    # x -= xoffset
    subtest = [0]
    usable = np.where(np.diff(y, 2) < dx ** 2)[0] + 1
    for part in partition(usable):
        if len(part) > 3:
            subx = x[part] + dx / 2
            subder = np.diff(y)[part]
            toret += list(polyfit(x[part], y[part], 3, graphing))
    return toret
    # for dyi in np.diff(y):
        
    


with open('C:/Users/Aaron2/Documents/Chemistry/Research/Leopold/neral/coadd_375k_citral_4-18GHz_80oC-01-input spectrum.spe', 'r') as f:
    x, y = np.array([line.split() for line in f], dtype = float).T



minheight = 0.0002

ranges = []
currlist = []
candinds = np.where(y > minheight)[0]



# plt.plot(x[candinds], y[candinds])

for ind1, ind2 in zip(candinds, candinds[1:]):
    currlist.append(ind1)
    if ind1 < ind2 - 3:
        ranges.append(currlist)
        currlist = []
currlist.append(ind2)
ranges.append(currlist)
ranges = [[412663, 412666, 412667, 412668, 412669, 412670, 412671, 412672, 412673, 412674, 412675, 412676, 412677, 412678, 412679, 412680, 412681, 412682, 412683, 412684, 412685, 412686, 412687, 412688, 412689, 412690, 412691, 412692, 412693, 412694, 412695, 412696, 412697, 412698]]
allpeaks = []
for rng in ranges:
    if len(rng) > 4:
        allpeaks += difffit(x[rng], y[rng], True)
        # if allpeaks[-1] == 8919.54654386868:
        #     print(rng)
        # plt.plot(x[rng], polyfit(x[rng], y[rng]))
plt.plot(x, y)

# testrng = ranges[811
# # polyfit(x[testrng], y[testrng])
# peaks = difffit(x[testrng], y[testrng])

# # plt.plot(x[testrng], polyfit(x[testrng], y[testrng]))

# plt.xlim(min(peaks) - 0.2, max(peaks) + 0.2)
# plt.ylim(-0.03, 0.04)
plt.xlim(8918, 8921)
plt.ylim(-0.01, 0.05)
plt.show()
