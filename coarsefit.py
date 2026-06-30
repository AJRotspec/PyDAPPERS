# -*- coding: utf-8 -*-
"""
Created on Sun May  4 16:54:45 2025

@author: Aaron2
"""
import numpy as np
from numpy.polynomial.polynomial import Polynomial as p
from Rotors import twomats

class coarsefittergeneral:

    kapnum = 3375
    def __init__(self, Jmax = 10):
        self.alllams = self.write_lookup(Jmax)
        
    def write_lookup(self, Jmax = 10):
        self.kappa = np.linspace(-1, 1, self.kapnum)
        Jmax += 1
        alllams = [[] for j in range(Jmax)]
        self.cat = twomats((2, 1, 1))
        for J in range(Jmax):
            self.cat[(J, J, 0)]
            self.cat[(J, J, 1)]
        for kap in self.kappa[:self.kapnum // 2 + 1]:
            self.cat.setkappa(kap)
            for J in range(Jmax):
                alllams[J] += [[self.cat._eigs[J][1][0]]]
                for ev, od in zip(self.cat._eigs[J][0], self.cat._eigs[J][1][1:]):
                    alllams[J][-1] += [ev]
                    alllams[J][-1] += [od]
        
        rawlist = []
        for level in alllams:
            rawlist += [[]]
            currlams = np.array(level).T
            for lams1, lams2 in zip(currlams, currlams[::-1]):
                rawlist[-1] += [list(lams1) + list(-lams2[:-1][::-1])]
        return rawlist


    # Make grid and kernel givin a list of arbitrary transitions

    def makekernel(self, translist):
        Jvec = np.array([tran[0][0] for tran in translist], dtype = float)
        Jmag = np.linalg.norm(Jvec)
        Jvec /= Jmag
        Evecs = []
        for (node1, node2) in translist:
            subE1 = np.array(self.alllams[node1[0]][node1[0] + node1[1] - node1[2]])
            subE2 = np.array(self.alllams[node2[0]][node2[0] + node2[1] - node2[2]])
            Evecs.append(subE1 - subE2)
        toret = []
        for vec in np.array(Evecs).T:
            overlap = np.dot(Jvec, vec)
            vec -= Jvec * overlap
            Emag = np.linalg.norm(vec)
            if Emag > 1e-12:
                vec /= Emag
                toret += [(vec, overlap, Emag)]
            else:
                toret += [(vec * 0, 1, 0)]

        self.currkern = (Jvec, Jmag, toret)
        self.gridmat = np.array([var[0] for var in toret])
        self.tree = gridvectree(self.gridmat, 15, 2)

    
    def usetree(self, series):
        n = len(series)
        # if (serstart, n) not in self.currkerns.keys():
        #     self.makekernel(progname, serstart, n)
        Jvec, Jmag, veclist = self.currkern#s[(serstart, n)]
        bestind = self.tree.use_tree(series)
        if bestind == 0:
            return {'rms': 1e8, 'A': 0, 'B': 0 , 'C': 0, 'num': 0}

        res = veclist[bestind]
        currres = (bestind, res[1], res[2], np.dot(series, res[0]))
        A = ((Jmag, currres[1]), (0, currres[2]))
        Adet = A[0][0] * A[1][1]
        solvec = (np.array(((A[1][1], -A[0][1]), (0, A[0][0]))) @ (np.dot(Jvec, series), currres[-1]) / Adet)
        A, C = np.array(((.5, 1), (.5, -1))) @ solvec
        B = (self.kappa[bestind] * (A - C) + A + C) * .5
        return {'rms': np.sqrt(np.linalg.norm(series) ** 2 - currres[-1] ** 2 - np.dot(Jvec, series) ** 2) / np.sqrt(n),
                'A':A, 'B': B, 'C': C, 'num': n
                }

    def usekernel(self, series):
        n = len(series)
        # if (serstart, n) not in self.currkerns.keys():
        #     self.makekernel(progname, serstart, n)
        Jvec, Jmag, veclist = self.currkern#s[(serstart, n)]
        currres = None
        grade = 64
        bestind = np.argmax(self.gridmat[::grade] @ series) * grade
        if bestind == 0:
            return {'rms': 1e8, 'A': 0, 'B': 0 , 'C': 0, 'num': 0}
        currres = None
        bestind = np.argmax(self.gridmat[bestind - grade: bestind + grade] @ series) + bestind - grade
        res = veclist[bestind]
        # print(bestind)
        currres = (bestind, res[1], res[2], np.dot(series, res[0]))
        A = ((Jmag, currres[1]), (0, currres[2]))
        Adet = A[0][0] * A[1][1]
        solvec = (np.array(((A[1][1], -A[0][1]), (0, A[0][0]))) @ (np.dot(Jvec, series), currres[-1]) / Adet)
        A, C = np.array(((.5, 1), (.5, -1))) @ solvec
        B = (self.kappa[bestind] * (A - C) + A + C) * .5
        return {'rms': np.sqrt(np.linalg.norm(series) ** 2 - currres[-1] ** 2 - np.dot(Jvec, series) ** 2) / np.sqrt(n),
                'A':A, 'B': B, 'C': C, 'num': n
                }
    def graph(self, series):
        n = len(series)
        # if (serstart, n) not in self.currkerns.keys():
        #     self.makekernel(progname, serstart, n)
        Jvec, Jmag, veclist = self.currkern#s[(serstart, n)]
        x, y = self.kappa[1:], self.gridmat[1:] @ series
        f = np.fft.rfft(y)
        f[100:] = 0
        yadj = np.fft.irfft(f)
        plt.plot(x, y)
        plt.plot(x, yadj)
        plt.ylim(263, 265)
        plt.xlim(-1, -.2)

class orthtransform:
    def __init__(self, n):
        self.n = n
        
    def make_vecs(self, numvecs):
        self.vecs = [np.ones((self.n,))]

class gridvectree:
    def __init__(self, grid, split = 5, depth = 4):
        self.grid = grid
        self.n = len(grid)
        self.split = split
        self.layers = []
        # print(self.n)
        for i in range(depth):
            self.layers.append(self.split_layer(i + 1))
        
    def split_layer(self, layer):
        reps = round(self.split ** layer)
        spacing = round(self.n / reps)
        # print(reps, spacing)
        return np.array([np.sum(self.grid[spacing * i: spacing * (i + 1)], axis = 0) for i in range(reps)])

    def use_tree(self, vec):
        layerinds = [0, -1]
        for i, layer in enumerate(self.layers):
            # reps = round(self.split ** i)
            # spacing = round(self.n / reps)
            bestind = np.argmax(layer[slice(*layerinds)] @ vec) + layerinds[0]
            layerinds = [max(self.split * bestind - 1, 0), min(self.split * (bestind + 1) + 1, self.n)]
            # print(bestind, layerinds)
        return np.argmax(self.grid[slice(*layerinds)] @ vec) + layerinds[0]
        

# if __name__ == '__main__':
#     tree = gridvectree(np.random.random((3125, 7)), 5, 4)
#     tree.use_tree(np.arange(7))
class progfitter:
    pathindex = twomats.progsT

    kapnum = 1601
    def __init__(self, Jmax = 35):
        self.alllams = self.write_lookup(Jmax)
        self.grids = {}
        self.currkerns = {}
    
    def write_lookup(self, Jmax = 35):
        self.kappa = np.linspace(-1, 1, self.kapnum)
        Jmax += 1
        alllams = [[] for j in range(Jmax)]
        cat = twomats((2, 1, 1))
        for J in range(Jmax):
            cat[(J, J, 0)]
            cat[(J, J, 1)]
        for kap in self.kappa[:self.kapnum // 2 + 1]:
            cat.setkappa(kap)
            for J in range(Jmax):
                alllams[J] += [[cat._eigs[J][1][0]]]
                for ev, od in zip(cat._eigs[J][0], cat._eigs[J][1][1:]):
                    alllams[J][-1] += [ev]
                    alllams[J][-1] += [od]
        
        rawlist = []
        for level in alllams:
            rawlist += [[]]
            currlams = np.array(level).T
            for lams1, lams2 in zip(currlams, currlams[::-1]):
                rawlist[-1] += [list(lams1) + list(-lams2[:-1][::-1])]
        return rawlist

    def grid_diff(self, trans):
        jtup, jtdown = tuple(map(twomats.JT, twomats.jkkreader(trans)))
        return np.array(self.alllams[jtup[0]][jtup[1]]) - np.array(self.alllams[jtdown[0]][jtdown[1]])
    

    # def generategrid(self, proglist):
    #     self.grid = 
    #     _, topind, botind = self.pathindex[progname]
    #     startJ = (botind + 1) // 2 + 1
    #     rawvecs = [np.array(lams2)[topind] - np.array(lams1)[botind] for lams1, lams2 in zip(self.alllams[startJ - 1:], self.alllams[startJ:])]
    #     self.grids = [None] * (startJ - 1) + rawvecs
    #     self.currkern = {}

    def make_kernel(self, tranlist):
        self.tranlist = tranlist
        Jvec = np.array([jkk1[0] * (jkk1[0] + 1) - jkk2[0] * (jkk2[0] + 1) for (jkk1, jkk2) in tranlist], dtype = float)
        Jmag = np.linalg.norm(Jvec)
        if Jmag < 1:
            raise Exception('magnitude of J vector suggests pure q branch transitions')
        Jvec /= Jmag
        Evecs = [self.grid_diff(tran) for tran in tranlist]
        toret = []
        for vec in np.array(Evecs).T:
            overlap = np.dot(Jvec, vec)
            vec -= Jvec * overlap
            Emag = np.linalg.norm(vec)
            if Emag > 1e-12:
                vec /= Emag
                toret += [(vec, overlap, Emag)]
            else:
                toret += [(vec * 0, 1, 0)]

        self.currkern = (Jvec, Jmag, toret)
        self.gridmat = np.array([var[0] for var in toret])
        
    def use_kernel(self, series):
        n = len(series)
        if n != len(self.tranlist):
            raise Exception('Wrong length of series.')
        # if (serstart, n) not in self.currkerns.keys():
        #     self.makekernel(progname, serstart, n)
        Jvec, Jmag, veclist = self.currkern#s[(serstart, n)]
        currres = None
        grade = 8
        bestind = np.argmax(self.gridmat[::grade] @ series) * grade
        if bestind == 0:
            return {'rms': 1e8, 'A': 0, 'B': 0 , 'C': 0, 'num': 0}
        currres = None
        bestind = np.argmax(self.gridmat[bestind - grade: bestind + grade] @ series) + bestind - grade
        Eperp, ov, Emag = veclist[bestind]
        Edot = np.dot(Eperp, series)
        A = ((Jmag, ov), (0, Emag))
        Adet = A[0][0] * A[1][1]
        solvec = (np.array(((A[1][1], -A[0][1]), (0, A[0][0]))) @ (np.dot(Jvec, series), Edot) / Adet)
        A, C = np.array(((1, 1), (1, -1))) @ solvec
        B = (self.kappa[bestind] * (A - C) + A + C) * .5
        return {'rms': np.sqrt(np.linalg.norm(series) ** 2 - Edot ** 2 - np.dot(Jvec, series) ** 2) / np.sqrt(n),
                'A':A, 'B': B, 'C': C, 'num': n
                }



from scipy.interpolate import CubicSpline as cs
class progfitter2:
    pathindex = twomats.progsT

    kapnum = 801
    def __init__(self):
        self.alllams = self.write_lookup()
        self.grids = {}
        self.currkerns = {}
        
    def write_lookup(self, Jmax = 20):
        self.kappa = np.linspace(-1, 1, self.kapnum)
        Jmax += 1
        alllams = [[] for j in range(Jmax)]
        cat = twomats((2, 1, 1))
        for J in range(Jmax):
            cat[(J, J, 0)]
            cat[(J, J, 1)]
        for kap in self.kappa[:self.kapnum // 2 + 1]:
            cat.setkappa(kap)
            for J in range(Jmax):
                alllams[J] += [[cat._eigs[J][1][0]]]
                for ev, od in zip(cat._eigs[J][0], cat._eigs[J][1][1:]):
                    alllams[J][-1] += [ev]
                    alllams[J][-1] += [od]
        
        rawlist = []
        for level in alllams:
            rawlist += [[]]
            currlams = np.array(level).T
            for lams1, lams2 in zip(currlams, currlams[::-1]):
                rawlist[-1] += [list(lams1) + list(-lams2[:-1][::-1])]
        return rawlist

    def generategrid(self, progname):
        topind, botind = self.pathindex[progname]
        startJ = (botind + 1) // 2 + 1
        rawvecs = [np.array(lams2)[topind] - np.array(lams1)[botind] for lams1, lams2 in zip(self.alllams[startJ - 1:], self.alllams[startJ:])]
        self.grids[progname] = [None] * (startJ - 1) + rawvecs
        self.currkerns[progname] = {}

    def makekernel(self, progname, startJ, length):
        Jvec = np.arange(length, dtype = float) + startJ
        Jmag = np.linalg.norm(Jvec)
        Jvec /= Jmag
        Evecs = self.grids[progname][startJ - 1: startJ - 1 + length]
        toret = []
        for vec in np.array(Evecs).T:
            overlap = np.dot(Jvec, vec)
            vec -= Jvec * overlap
            Emag = np.linalg.norm(vec)
            if Emag > 1e-12:
                vec /= Emag
                toret += [(vec, overlap, Emag)]
            else:
                toret += [(vec * 0, 1, 0)]
        self.currkerns[progname][(startJ, length)] = (Jvec, Jmag, toret)
        
    def usekernel(self, progname, serstart, series):
        n = len(series)
        if (serstart, n) not in self.currkerns[progname].keys():
            self.makekernel(progname, serstart, n)
        Jvec, Jmag, veclist = self.currkerns[progname][(serstart, n)]
        currres = None
        grade = 4
        for i, (vec, ov, Emag) in enumerate(veclist[::grade * 2]):
            newres = (i, np.dot(series, vec))
            if currres == None:
                currres = newres
            if newres[-1] > currres[-1]:
                currres = newres
        bestind = currres[0] * grade * 2
        if bestind == 0:
            return {'rms': 1e8, 'A': 0, 'B': 0 , 'C': 0, 'num': 0}
        currres = None
        for i, (vec, ov, Emag) in enumerate(veclist[bestind - grade: bestind + grade]):
            newres = (i, ov, Emag, np.dot(series, vec))
            if currres == None:
                currres = newres
            if newres[-1] > currres[-1]:
                currres = newres
        bestind = currres[0] + bestind - grade
        A = ((Jmag, currres[1]), (0, currres[2]))
        Adet = A[0][0] * A[1][1]
        solvec = (np.array(((A[1][1], -A[0][1]), (0, A[0][0]))) @ (np.dot(Jvec, series), currres[-1]) / Adet)
        A, C = np.array(((.5, 1), (.5, -1))) @ solvec
        B = (self.kappa[bestind] * (A - C) + A + C) * .5
        return {'rms': np.sqrt(np.linalg.norm(series) ** 2 - currres[-1] ** 2 - np.dot(Jvec, series) ** 2) / np.sqrt(n),
                'A':A, 'B': B, 'C': C, 'num': n
                }
    
