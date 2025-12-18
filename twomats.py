# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 10:19:33 2025

@author: Aaron2
"""

import numpy as np
from numpy.polynomial.polynomial import Polynomial as p
from spfitspcat import progsT as progdic

class twomats:
    progsT = {'Ra J0J': (1, 0, 0), 'Ra J1J-': (1, 1, 1), 'Ra J1J+': (1, 2, 2), 
              'Ra J2J-': (1, 3, 3), 'Ra J2J+': (1, 4, 4), #'QbJ1J-': (0, 2, 0),
              'Rb J0J': (1, 0, 1), 'Rb J1J': (1, 1, 0), 'Rb 220': (1, 4, 1),
              'Rb 221': (1, 3, 2), 'Rb 330': (1, 6, 3), 'Rb 331': (1, 5, 4),
              'Rc 220': (1, 4, 2), 'Rc 221': (1, 3, 1)
                 }

    @staticmethod
    def JKK(J, T):       
        return (J, (T + 1) // 2, (2 * J - T + 1) // 2)

    @staticmethod
    def progify(jkk1, jkk2):
        toret = [jkk1[0] - jkk2[0]]
        toret.append(jkk1[1] * 2 - (jkk1[0] + jkk1[1] + jkk1[2]) % 2)
        toret.append(jkk2[1] * 2 - (jkk2[0] + jkk2[1] + jkk2[2]) % 2)
        return tuple(toret)

    class node:
        def __init__(self, jkk, parent):
            if jkk[0] != jkk[1] + jkk[2]:
                if jkk[0] != jkk[1] + jkk[2] - 1:
                    print('Invalid quantum numbers')
                    return
            self.parent = parent
            self.J, self.subind = parent.indfinder(jkk)
            self.sym = parent.symlabel(jkk)
            self.tau = jkk[1] - jkk[2]

        @property
        def Ekap(self):
            return self.parent._eigs[self.J][self.sym // 2][self.subind]
        
        @property
        def E(self):
            return (self.parent.ABC[0] + self.parent.ABC[2]) / 2 * self.J *(self.J + 1) + (
                self.parent.ABC[0] - self.parent.ABC[2]) / 2 * self.Ekap
    
        @property
        def vec(self):
            return self.parent._vecs[self.J][self.sym // 2][:, self.subind]
        
        @property
        def Ekapder(self):
            pert = [i ** 2 for i in range(-self.J + 1 - self.sym // 2, self.J + self.sym // 2, 2)]
            return np.dot(self.vec, pert * self.vec)
        
        @property
        def grad(self):
            dEk = (self.parent.ABC[0] - self.parent.ABC[2]) / 2 * self.Ekapder * self.parent.dkappa
            dJ2 = np.array([1, 0, 1]) / 2 * self.J * (self.J + 1)
            dAminC = np.array([1, 0, -1]) / 2 * self.Ekap
            return dJ2 + dEk + dAminC
        @property
        def Ekap2(self):
            toret = 0
            pert = [i ** 2 for i in range(-self.J + 1 - self.sym // 2, self.J + self.sym // 2, 2)]
            for eig, vec in zip(self.parent._eigs[self.J][self.sym // 2], self.parent._vecs[self.J][self.sym // 2].T):
                if eig == self.Ekap:
                    pass
                else:
                    toret += np.dot(self.vec, pert * vec) ** 2 / (self.Ekap - eig)
            return toret
            

    class edge:
        def __init__(self, tran, parent):
            self.parent = parent
            self.node1 = self.parent[tran[0]]
            self.node2 = self.parent[tran[1]]
            # self._nu = 0
            self.sym = self.node1.sym * 4 + self.node2.sym
            self.type = self.parent.transtype(tran[0], tran[1])
            self.obs = None
        @property
        def nu(self):
            return self.node1.E - self.node2.E
        @property
        def grad(self):
            return self.node1.grad - self.node2.grad
        @property
        def E2(self):
            return self.node1.Ekap2 - self.node2.Ekap2
            
    numinds = 3
    def __init__(self, ABC, temp = 2, dipole = (1, 1, 1), bulkpopulate = False):
        self.ABC = np.array(ABC)
        self.AC = float(self.ABC[0] - self.ABC[2])
        self.Rp = (np.roll(self.ABC, 1) - np.roll(self.ABC, 2)) / self.AC
        self.kappa = (2 * self.ABC[1] - self.ABC[0] - self.ABC[2]) / self.AC      
        self._nodes = {}
        self._edges = {}
        self.temp = temp
        self.dipole = dipole
        self._matels = [([0],[])]
                       
        self._vecs = [[(None,), [[1]],]]
                      # [(None,), (None,)]]
        self._eigs = [[(None,), (None,)]]
                      # [(None,), (None,)]]
        self._dkappa = 0
        
    @staticmethod
    def symlabel(jkk):
        #overhaul, 2s digit corrsponds to matrix size: 1 for larger, 0 for smaller
        # More compact: first submatrix size = J + symlabel // 2
        if (jkk[0] + jkk[1] + jkk[2]) % 2:
            toret = 0b00
        else:
            toret = 0b10
        # The eigenvector evenness is shared by the second numeral of the binary symlabel
        if (jkk[0] - jkk[1]) % 2:
            toret += 0b1
        else:
            toret += 0b0
        return toret

    
    def __getitem__(self, jkk):
        jkk = self.jkkreader(jkk)
        if jkk[1] == ():
            if jkk[0] not in list(self._nodes.keys()):
                self.define_node(jkk[0])
            return self._nodes[jkk[0]]
        if jkk not in list(self._edges.keys()):
            self.define_edge(jkk)
        return self._edges[jkk]

    def define_node(self, jkk):
        newnode = self.node(jkk, self)
        J = newnode.J
        sym = newnode.sym
        while len(self._matels) <= J:
            self._matels += [None]
            self._vecs += [[[None] for i in range(2)]]
            self._eigs += [[[None] for i in range(2)]]
        if not self._matels[J]:
            self.makematels(J)
        if self._eigs[J][sym // 2][0] == None:
            self._eigs[J][sym // 2], self._vecs[J][sym // 2] = \
            np.linalg.eigh(self.makemat(*self._matels[J], sym))
        self._nodes[jkk] = newnode
    
    def makemat(self, A, B, sym):
        if A == [0]:
            return [[0]]
        matsize = sym // 2 + len(A)
        if matsize % 2:
            a = [ai * self.kappa for ai in A[1::2]]
            b = B[1::2]
        else:
            a = [ai * self.kappa for ai in A[::2]]
            b = B[::2]
        mat = np.asarray(np.diag(a), dtype = float)
        
        mat[1:, :-1] += np.diag(b)
        mat[:-1, 1:] += np.diag(b)
        return mat
    
    
    def makematels(self, J):
        def f(J, n):
            return (J * (J + 1) - n * (n + 1)) * (J * (J + 1) - n * (n - 1))
        A = [K ** 2 for K in range(-J, J + 1)]
        B = [.5 * np.sqrt(f(J, K)) for K in range(-J + 1, J)]
        self._matels[J] = (A, B)
        
    def fullmat(self, J, parity):
        def f(J, n):
            return (J * (J + 1) - n * (n + 1)) * (J * (J + 1) - n * (n - 1))
        A = [K ** 2 * self.kappa for K in range(-J + 1 - parity, J + parity, 2)]
        B = [.5 * np.sqrt(f(J, K)) for K in range(-J + 2 - parity, J - 1 + parity, 2)]
        mat = np.asarray(np.diag(A), dtype = float)
        
        mat[1:, :-1] += np.diag(B)
        mat[:-1, 1:] += np.diag(B)
        return mat

    
    def define_edge(self, tran):
        for jkk in tran:
            if jkk not in list(self._nodes.keys()):
                self.define_node(jkk)
        self._edges[tran] = self.edge(tran, self)
        
            
    @staticmethod
    def indfinder(jkk):
        return jkk[0], (jkk[0] + jkk[1] - jkk[2]) // 2

    @staticmethod
    def transtype(jkk1, jkk2):
        if jkk1[0] > jkk2[0]:
            branch = 'r'
        elif jkk1[0] == jkk2[0]:
            branch = 'q'
        else:
            branch = 'p'
        dka = (jkk1[1] - jkk2[1]) % 2
        dkp = (jkk1[2] - jkk2[2]) % 2
        if dka and dkp:
            typ = 'b'
        elif dka:
            typ = 'c'
        else:
            typ = 'a'
        return (typ, branch)

    def setkappa(self, newkappa):
        self.kappa = newkappa
        for J in range(len(self._eigs)):
            for sym, eigs in enumerate(self._eigs[J]):                
                if not eigs[0] == None:
                    self._eigs[J][sym], self._vecs[J][sym] = np.linalg.eigh(self.makemat(*self._matels[J], sym * 2))
            
    @property
    def dkappa(self):
        return np.array([2 * (self.ABC[2] - self.ABC[1]) / (self.ABC[0] - self.ABC[2]) ** 2,
                         2 / (self.ABC[0] - self.ABC[2]),
                         2 * (self.ABC[1] - self.ABC[0]) / (self.ABC[0] - self.ABC[2]) ** 2])
    
    def setABC(self, newABC):
        # Sets a completely new set of ABC, recalculates all roots
        self.ABC = np.array(newABC)
        self.setkappa((2 * self.ABC[1] - self.ABC[0] - self.ABC[2]) / (self.ABC[0] - self.ABC[2]))     
    
    def updateABC(self, deltaABC):
        # Nudges ABC a bit, uses the perturbative expansion to
        # start guesses of zeros
        self.massgrad()
        self.ABC += np.array(deltaABC)
        self.kappa = (2 * self.ABC[1] - self.ABC[0] - self.ABC[2]) / (self.ABC[0] - self.ABC[2])      


    
    @classmethod
    def jkkreader(cls, jkk):
        if type(jkk) == str:
            jkk = tuple(map(int, jkk.split()))
        if len(jkk) == 2:
            jkk1, jkk2 = jkk
        else:
            jkk1 = jkk[:cls.numinds]
            jkk2 = jkk[cls.numinds:]
        return tuple(jkk1), tuple(jkk2)
    def fitter(self, eject = False, constraint = 1e3 * np.ones((3,))):
        bounds = np.array([self.ABC * (1 - constraint), self.ABC * (1 + constraint)])
        # Must be run after giving the 'obs' attribute to all edges
        for i in range(10):
            ers = []
            jac = []
            for edge in self._edges.values:
                jac += [edge.grad]
                ers += [edge.obs - edge.nu]
            jac = np.array(jac)
            # try:
            upd = np.linalg.solve(jac.T@jac, jac.T @ers)
            # except:
            #     upd = np.ones((3, )) * .001
            
            
            if np.linalg.norm(upd) < 1e-10:
                break
            newABC = self.ABC + upd
            newABC = np.max([newABC, bounds[0]], axis = 0)
            newABC = np.min([newABC, bounds[1]], axis = 0)
            self.setABC(newABC)
        
        
        stdev = np.linalg.norm(ers)
        # if eject:
        #     for er, trans in zip(ers, assigned):
        #         if er > eject:
        #             self.remove_transition(trans)
        #     return self.fitter()
        return self.ABC, np.sqrt(np.diagonal(np.linalg.inv(jac.T@jac)) / len(ers)) * stdev,\
            np.linalg.norm(ers) / np.sqrt(len(ers)), ers

