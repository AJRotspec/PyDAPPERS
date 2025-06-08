# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 10:37:20 2024

@author: Aaron2
"""

from spfitspcat import CatFile, LinFile, progsT, JKK
import numpy as np
import time
import matplotlib.pyplot as plt
# from layereddigraph import LayeredDiGraph


# Each item in progsT is a 3-tuple, the firt element representing delta J, 
# the second is T for the upper state, and the third T for the lower

progsT = {'Ra J0J': (1, 0, 0), 'Ra J1J-': (1, 1, 1), 'Ra J1J+': (1, 2, 2), 
          'Ra J2J-': (1, 3, 3), 'Ra J2J+': (1, 4, 4), #'QbJ1J-': (0, 2, 0),
          'Rb J0J': (1, 0, 1), 'Rb J1J': (1, 1, 0), 'Rb 220': (1, 4, 1),
          'Rb 221': (1, 3, 2), 'Rb 330': (1, 6, 3), 'Rb 331': (1, 5, 4),
          'Rc 220': (1, 4, 2), 'Rc 221': (1, 3, 1)
             }

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
        self.nodes[layer][u] = {'out': (), 'in': (), **kwargs}

    def add_edge(self, lowerlayer, u, v, **kwargs):
        if not u in self.nodes[lowerlayer].keys():
            self.add_node(lowerlayer, u)
        if not v in self.nodes[lowerlayer + 1].keys():
            self.add_node(lowerlayer + 1, v)
        self.edges[lowerlayer][(u, v)] = kwargs
        self.nodes[lowerlayer][u]['out'] += (v,)
        self.nodes[lowerlayer + 1][v]['in'] += (v,)

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
                
    def DFS(self):
        paths = []
        for i, layer in enumerate(self.nodes[:-1]):
            for node, dic in layer.items():
                if not dic['in']:
                    for newpath in self.depthsearchrecursion(i, node, dic['out']):
                        toadd = newpath[0]
                        for node in newpath[1:]:
                            toadd += (node[-1],)
                        paths.append((i, toadd))
        
        paths.sort(reverse = True, key = lambda x: len(x[1]))
        best = len(paths[0][-1])
        # print(best)
        for i, path in enumerate(paths):
            if len(path[-1]) < best:
                break
        return paths[:i]
    def depthsearchrecursion(self, currlayer, currnode, outs):  
        if not outs:
            return [[currnode]]
        toret = []
        for out in outs:
            nextouts = self.nodes[currlayer + 1][out]['out']
            for path in self.depthsearchrecursion(currlayer + 1, out, nextouts):
                toret.append([currnode] + path)
        return toret
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
        

    
class fitfinder:
    
    def __init__(self, startwin, ratwin, derwin, prog, specwindow, fileloc = 'activememory\\'):        
        self.prog = prog
        cat = CatFile(fileloc + 'base.cat')
        self.startwin = startwin
        self.ratwin = ratwin
        if derwin:
            self.derwin = derwin
        else:
            # Arbitrary large value
            self.derwin = 100

        with open(fileloc + 'peaklist.txt', 'r') as f:
            self.peaks = np.array(f.readlines(), dtype = float)
        progtranses = []
        self.progjkk = []
        for trans in cat.transes:
            if specwindow[0] < trans[-2] < specwindow[1]:
                if trans[3] == progsT[prog]:
                    progtranses += [trans]
                    self.progjkk += [tuple(trans[1] + trans[2])]
        self.preds = [trans[-2] for trans in progtranses]
        
        
        self.J0 = self.progjkk[0][0]
        self.span = self.progjkk[-1][0] - self.J0 + 1
        (dJ, T1, T2) = progsT[self.prog]
        self.jkk = [JKK(i + self.J0, T1) + JKK(i - dJ + self.J0, T2) for i in range(self.span)]

        self.buildnet()
        self.builddernet()
        self.paths = [[(jkk, peak) for jkk, peak in zip(self.jkk[path[0]:], path[1])]
                      for path in self.dernet.DFS()]
        self.maxpath = len(self.paths[0])
        
    
    
    def writelins(self):
        indops = progsT[self.prog]
        for i, path in enumerate(self.paths):
            writelist = []
            newlin = LinFile(f'activememory\\basefitbank\\{self.prog}_{i}.lin')
            for J, peak in enumerate(path[1]):
                jkk = self.JKK(J + self.J0 + path[0], indops[1]) + self.JKK(J - indops[0], indops[2])
                writelist += [(peak, jkk)]
            newlin.assign(writelist)
            newlin.makefile()
            # print(f'activememory\\basefitbank\\{self.prog}_{i}.lin')
    
    def buildnet(self):     
        self.net = LayeredDiGraph(self.span)
        for jkk, pred in zip(self.progjkk, self.preds):
            for peak in self.peaks:
                if pred - self.startwin < peak:
                    if pred + self.startwin < peak:
                        break
                    self.net.add_node(jkk[0] - self.J0, peak)
                    
        # Make initial self.network based on ratio test
        # print(len(self.net.nodes))
        for j, (pred1, layer1, pred2, layer2) in enumerate(zip(self.preds[:-1], self.net.nodes[:-1], 
                                                                self.preds[1:], self.net.nodes[1:])):
            ordered1 = sorted(layer1.keys())
            ordered2 = sorted(layer2.keys())
            for obs1 in ordered1:
                rat1 = obs1 / pred1
                for obs2 in ordered2:
                    er = rat1 * pred2 - obs2
                    if er < self.ratwin:
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
                    for obs3 in obs3s:
                        if abs(rat * (pred3 - pred2) + obs2 - obs3) < self.derwin:
                            self.dernet.add_edge(j, (obs1, obs2), (obs2, obs3))

    @staticmethod
    def JKK(J, T):       
        return (J, (T + 1) // 2, (2 * J - T + 1) // 2)
    def pathcleanup(self, startJ, peaks):
        (dJ, T1, T2) = progsT[self.prog]
        startJ += self.J0
        return [(self.JKK(i + startJ, T1) + self.JKK(i - dJ + startJ, T2), peak) for i, peak in enumerate(peaks)]
        
if __name__ == '__main__':
    # findnet = fitfinder(100, 10, 0, 'Ra J1J-', (6000, 18000), 'dummymem\\')
    sttime = time.time()
    findnet = fitfinder(1000, 100, 10, 'Rb J1J', (4000, 12000), 'activememory\\')
    print(time.time() - sttime)
    # print(len(findnet.paths))
    # paths = findnet.pathfinder()
    # print(len(findnet.net.edges))
    # findnet.net.graph['trans'][(5, 0, 5, 4, 0, 4)]))
    # print(len(findnet.net.graph['trans'][(11, 0, 11, 10, 0, 10)]))
    # fig, ax, lc = findnet.plotnet()
    # rawpoints = nx.dag_longest_path(findnet.net)
    
    # xs = np.array([point[1][0] for point in rawpoints])
    # ys = np.array([point[0] / findnet.net.nodes[point]['pred'] for point in rawpoints])
    # plt.scatter(xs, ys)
    # from numpy.polynomial.polynomial import Polynomial as p
    # fit = p(list(reversed(np.polyfit(xs, ys, 3))))
    # print(fit)
    # xfine = np.linspace(4, 11, 100)
    # plt.plot(xfine, fit(xfine))

