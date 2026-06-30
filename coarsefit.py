# -*- coding: utf-8 -*-
"""
Created on Sun May  4 16:54:45 2025

@author: Aaron2
"""
import numpy as np
from numpy.polynomial.polynomial import Polynomial as p
from Rotors import twomats

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


    
