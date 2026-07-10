# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 10:37:20 2024

@author: Aaron2
"""

from spfitspcat import CatFile, LinFile
from Rotors import twomats
import numpy as np
import time
import matplotlib.pyplot as plt
from functools import cache, lru_cache
import os
# from scipy.sparse import coo_array
# from layereddigraph import LayeredDiGraph


# Each item in progsT is a 3-tuple, the first element representing delta J, 
# the second is T for the upper state, and the third T for the lower


class LayeredDiGraph:
    def __init__(self, layers):
        if type(layers) == int:
            layers = [i for i in range(layers)]
        self.layers = layers
        self.nodes = [{} for layer in layers]
        self.edges = [{} for layer in layers[:-1]]

    def nodes(self, layer, u):
        return self.nodes[layer][u]
    def allnodes(self):
        toret = []
        for i, nodes in enumerate(self.nodes):
            for node, dic in nodes.items():
                toret += [(i, node, dic)]
        return toret

    def add_node(self, layer, u, **kwargs):
        self.nodes[layer][u] = {'out': [], 'in': [], **kwargs}

    def add_edge(self, lowerlayer, u, v, **kwargs):
        if not u in self.nodes[lowerlayer]:
            self.add_node(lowerlayer, u)
        if not v in self.nodes[lowerlayer + 1]:
            self.add_node(lowerlayer + 1, v)
        self.edges[lowerlayer][(u, v)] = kwargs
        self.nodes[lowerlayer][u]['out'].append(v)
        self.nodes[lowerlayer + 1][v]['in'].append(u)
    
    def remove_node(self, layer, u):
        edges_in = self.nodes[layer][u]['in']
        edges_out = self.nodes[layer][u]['out']
        del self.nodes[layer][u]
        for edge in edges_in:
            self.remove_edge(layer - 1, edge, u)
        for edge in edges_out:
            self.remove_edge(layer, u, edge)
    
    def remove_edge(self, lowerlayer, u, v):
        del self.edges[lowerlayer][(u, v)]
        if u in self.nodes[lowerlayer]:
            self.nodes[lowerlayer][u]['out'].remove(v)
        if v in self.nodes[lowerlayer + 1]:
            self.nodes[lowerlayer + 1][v]['in'].remove(u)
            
    
    
    def deriv(self):
        def nodemerge(node1, node2):
            return node1 + node2[-1:]
        
        toret = LayeredDiGraph(self.layers[-1])            
        for layer, edges in enumerate(self.edges):
            for edge in edges.keys():
                node1 = nodemerge(*edge)
                toret.add_node(layer, node1)
                for out in self.nodes[layer + 1][edge[1]]['out']:
                    toret.add_edge(layer, node1, nodemerge(edge[1], out))
        return toret
    
    def draw(self):
        points = []
        if type(list(self.nodes[0].keys())[0]) == tuple:
            nodeval = lambda x: x[0]
        else:
            nodeval = lambda x: x
        means = []
        for i, nodes in enumerate(self.nodes):
            ys = np.array([nodeval(node) for node in nodes.keys()])
            means += [np.mean(ys)]
            ys -= np.mean(ys)

            points += [(i, y) for y in ys]
        linecol = []
        for i, edges in enumerate(self.edges):
            for edge in edges.keys():
                linecol += [((i, nodeval(edge[0]) - means[i]),
                             (i + 1, nodeval(edge[1]) - means[i + 1]))] 
        # print(linecol)
        plt.scatter(*np.array(points).T)
        for line in linecol:
            plt.plot(*np.array(line).T, color = 'k')
        plt.show()
        # ax.add_collection(LineCollection(linecol))
                
    def DFS(self, startlayer = None, endlayer = None):
        if not startlayer:
            startlayer = self.layers[0]
        if not endlayer:
            endlayer = self.layers[-1]

        @cache
        def recur_DFS(currlayer, currnode, endlayer): 
            # print(currlayer, currnode) 
            if currlayer == endlayer:
                return [[currnode]]
            toret = []
            for out in self.nodes[currlayer][currnode]['out']:
                for path in recur_DFS(currlayer + 1, out, endlayer):
                    toret.append([currnode] + path)
                    # yield [currnode] + path
            return toret

        for node in self.nodes[startlayer]:
            for newpath in recur_DFS(startlayer, node, endlayer):
                toadd = newpath[0]
                for node in newpath[1:]:
                    toadd += (node[-1],)
                yield (startlayer, toadd)
        

    def connected_layer_sets(self):
        if self.DFS_connectivity():
            return [(self.layers[0], self.layers[-1])]
        for toplayer in self.layers[::-1][1:]:
            if self.DFS_connectivity((self.layers[0], toplayer)):
                break
        for bottomlayer in self.layers[1:]:
            if self.DFS_connectivity((bottomlayer, self.layers[-1])):
                break
        return 
    def largest_layer_set(self):
        if self.DFS_connectivity():
            return {(self.layers[0], self.layers[-1])}
        lower = iter(self.layers)
        upper = iter(self.layers[::-1])
        prevlow = next(lower)
        currlow = next(lower)
        prevup = next(upper)
        currup = next(upper)

        

    def DFS_connectivity(self, bounds):
        bounds = (self.layers[0], self.layers[-1])
        currmax = 0
        @cache
        def recursion(currlayer, currnode):
            nonlocal currmax, bounds
            if currlayer == bounds[-1]:
                return True
            for out in self.nodes[currlayer][currnode]['out']:
                if recursion(currlayer + 1, out):
                    return True
            if not self.nodes[currlayer][currnode]['out']:
                currmax = max((currmax, currlayer - bounds[0]))
            return False
        for node in self.nodes[bounds[0]]:
            if recursion(0, node):
                return True, bounds[-1] - bounds[0]
        return False, currmax

                


    def adjsubs(self):
        nodeinds = []
        dims = []
        for layer in self.nodes:
            nodeinds += [{node: i for i, node in enumerate(layer.keys())}]
            dims.append(len(layer))
        toret = []
        for layer, befnodes, endnodes, befdim, enddim in zip(self.edges, nodeinds[:-1], nodeinds[1:], dims[:-1], dims[1:]):
            sub = np.zeros((befdim, enddim), dtype = int)
            for edge in layer.keys():
                sub[befnodes[edge[0]], endnodes[edge[1]]] = 1
            toret += [sub]
        return toret
    
    def connected_layers(self):
        seennodes = [set(node for node in self.nodes[0])]
        for layer in self.layers[:-1]:
            seen = set()
            for node in seennodes[-1]:
                for newnode in self.nodes[layer][node]['out']:
                    seen.add(newnode)
            seennodes.append(seen)
        # print([len(sub) for sub in seennodes])
    
    def connectivity_matrices(self):
        inddicts = [{node: i for i, node in enumerate(layer)} for layer in self.nodes[1:]]
        toret = []
        for layer, nextlayer in zip(self.nodes, inddicts):
            newarr = np.zeros(shape = (len(layer), len(nextlayer)), dtype = int)
            for u, dic in enumerate(layer.values()):
                for v in dic['out']:
                    newarr[u, nextlayer[v]] = 1
            toret.append(newarr)
        return toret
    
    def pathcount(self):
        # This method is VERY inefficient
        mats = self.connectivity_matrices()
        mat = mats[0]
        for nextmat in mats[1:]:
            mat = mat @ nextmat
        return np.sum(mat)


class fitfinder:

    def __init__(self, startwin, ratwin, derwin, prog, specwindow, fileloc = 'activememory', coarsefitter = None, coarsecut = 1):        
        currtime = time.time()
        self.prog = prog

        self.startwin = startwin
        self.ratwin = ratwin
        if derwin:
            self.derwin = derwin
        else:
            # Arbitrary large value
            self.derwin = 100

        with open(os.path.join(fileloc, 'peaklist.txt'), 'r') as f:
            self.peaks = np.array(f.readlines(), dtype = float)

        self.progjkk = []
        self.loadpreds(fileloc, specwindow, prog)
        newtime = time.time()
        print(f'Read cat file: {newtime - currtime:.02} s')
        currtime = newtime

        self.buildnet()
        newtime = time.time()
        print(f'Build ratio net: {newtime - currtime:.02} s')
        currtime = newtime

        self.builddernet()
        newtime = time.time()
        print(f'Build derivative net: {newtime - currtime:.02} s')
        currtime = newtime
        
        connected, depth = self.dernet.DFS_connectivity((self.dernet.layers[0], self.dernet.layers[-1]))
        if not connected:
            raise Exception('Paths not connected - use less stringent windows or smaller frequency range.')
        
        newtime = time.time()
        print(f'Check connectivity: {newtime - currtime:.02} s')
        currtime = newtime

        self.prunedernet()
        newtime = time.time()
        print(f'Prune dernet: {newtime - currtime:.02} s')
        currtime = newtime

        if coarsefitter != None:
            self.getfits_coarsefit(coarsefitter, coarsecut)
        else:
            self.getfits_nocoarsefit()

        
        newtime = time.time()
        print(f'Found all paths: {newtime - currtime:02f} s')
        currtime = newtime
        try:
            self.maxpath = len(self.paths[0])
        except IndexError:
            raise Exception('No fits found')
        
        self.writelins()
        newtime = time.time()
        print(f'Wrote all .lin files: {newtime - currtime:02f} s')
        currtime = newtime

    def loadpreds(self, fileloc, specwindow, prog):
        cat = CatFile(os.path.join(fileloc, 'base.cat'))
        progtranses = []
        for trans in cat.transes:
            if specwindow[0] < trans[-2] < specwindow[1]:
                if trans[3] == twomats.progsT[prog]:
                    progtranses.append(trans)
                    self.progjkk += [tuple(trans[1] + trans[2])]
        self.preds = [trans[-2] for trans in progtranses]
        self.transes= [(trans[1], trans[2]) for trans in progtranses]
        self.J0 = self.progjkk[0][0]
        self.span = self.progjkk[-1][0] - self.J0 + 1
        # (dJ, T1, T2) = twomats.progsT[self.prog]
        # self.jkk = [twomats.JKK(i + self.J0, T1) + twomats.JKK(i - dJ + self.J0, T2) for i in range(self.span)]

    
    def writelins(self):
        for i, path in enumerate(self.paths):
            writelist = []
            newlin = LinFile(os.path.join('activememory', 'basefitbank', f'{self.prog}_{i}.lin'))
            newlin.assign([(pair[1], list(pair[0][0]) + list(pair[0][1])) for pair in path])
            newlin.makefile()
            # print(os.path.join('activememory', 'basefitbank', f'{self.prog}_{i}.lin'))
    
    def buildnet(self):     
        self.net = LayeredDiGraph(self.span)
        currstart = 0
        for jkk, pred in zip(self.progjkk, self.preds):
            changed = False
            for i, peak in enumerate(self.peaks[currstart:]):    
                if pred - self.startwin < peak:
                    if not changed:
                        currstart += i
                        changed = True
                    if pred + self.startwin < peak:
                        break
                    self.net.add_node(jkk[0] - self.J0, peak)
        # Make initial self.network based on ratio test
        trycount = 0
        for j, (pred1, layer1, pred2, layer2) in enumerate(zip(self.preds[:-1], self.net.nodes[:-1], 
                                                                self.preds[1:], self.net.nodes[1:])):
            ordered1 = sorted(layer1.keys())
            ordered2 = sorted(layer2.keys())
            currstart = 0
            for obs1 in ordered1:
                changed = False
                rat1 = obs1 / pred1
                for i, obs2 in enumerate(ordered2[currstart:]):
                    trycount += 1
                    er = rat1 * pred2 - obs2
                    if er < self.ratwin:
                        if not changed:
                            currstart += i
                            changed = True
                        if er < - self.ratwin:
                            break
                        self.net.add_edge(j, obs1, obs2)

    def builddernet(self):
        self.dernet = LayeredDiGraph(self.span - 1)
        for j, (pred1, pred2, pred3, layer1) in enumerate(zip(self.preds[:-2], self.preds[1:-1],
                                                              self.preds[2:], self.net.nodes[:-2])):
            for obs1, dic in layer1.items():
                for obs2 in dic['out']:
                    obs3s = self.net.nodes[j + 1][obs2]['out']
                    rat = (obs2 - obs1) / (pred2 - pred1)
                    derpred = rat * (pred3 - pred2) + obs2
                    for obs3 in obs3s:
                        if abs(derpred - obs3) < self.derwin:
                            self.dernet.add_edge(j, (obs1, obs2), (obs2, obs3))

    def prunedernet(self):
        deleted = 0
        for layer, nodes in zip(self.dernet.layers[-2::-1], self.dernet.nodes[-2::-1]):
            for node, adj in list(nodes.items()):
                if not adj['out']:
                    self.dernet.remove_node(layer, node)
                    deleted += 1
        print(deleted)

    def getfits_nocoarsefit(self):
        self.paths = []
        self.totpathnum = 0
        for path in self.dernet.DFS():
            self.totpathnum += 1
            # print(fitter.usekernel(path[1]))
            self.paths.append([(jkk, peak) for jkk, peak in zip(self.transes, path[1])])


    def getfits_coarsefit(self, fitter, coarsecut):
        self.paths = []
        self.totpathnum = 0
        fitter.make_kernel(self.transes)
        for path in self.dernet.DFS():
            self.totpathnum += 1
            if fitter.use_kernel(path[1])['rms'] < coarsecut:
                self.paths.append([(jkk, peak) for jkk, peak in zip(self.transes, path[1])])


