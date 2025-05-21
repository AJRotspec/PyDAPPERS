# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 10:37:20 2024

@author: Aaron2
"""

from spfitspcat import CatFile, LinFile
import numpy as np
import time
import matplotlib.pyplot as plt
# from layereddigraph import LayeredDiGraph

maxJ = 100
progressions = {'Ra J0J':[[i + 1, 0, i + 1, i, 0, i] for i in range(maxJ)],
                'Ra J1J-':[[i + 1, 1, i + 1, i, 1, i] for i in range(maxJ)],
                'Ra J1J+':[[i + 2, 1, i + 1, i + 1, 1, i] for i in range(maxJ)],
                'Ra J2J-':[[i + 2, 2, i + 1, i + 1, 2, i] for i in range(maxJ)],
                'Ra J2J+':[[i + 3, 2, i + 2, i + 2, 2, i] for i in range(maxJ)],
                'Rb J1J': [[i + 1, 1, i + 1, i, 0, i] for i in range(maxJ)],
                'Rb J0J': [[i + 1, 0, i + 1, i, 1, i] for i in range(maxJ)],
                'Rb 220': [[i + 2, 2, i, i + 1, 1, i + 1] for i in range(maxJ)],
                'Rb 221': [[i + 2, 2, i + 1, i + 1, 1, i] for i in range(maxJ)],
                'Rb 330': [[i + 3, 3, i, i + 2, 2, i + 1] for i in range(maxJ)],
                'Rb 331': [[i + 3, 3, i + 1, i + 2, 2, i] for i in range(maxJ)],
                'Rc 110': [[i + 1, 1, i, i, 0, i] for i in range(maxJ)],
                'Rc J0J': [[i + 2, 0, i + 2, i + 1, 1, i] for i in range(maxJ)],
                'Rc 221': [[i + 2, 2, i + 1, i + 1, 1, i + 1] for i in range(maxJ)],
                'Rc 220': [[i + 2, 2, i, i + 1, 1, i] for i in range(maxJ)],
                'Rc 331': [[i + 3, 3, i + 1, i + 2, 2, i + 1] for i in range(maxJ)],
                'Rc 330': [[i + 3, 3, i, i + 2, 2, i] for i in range(maxJ)],
                'Qa 221': [[i + 2, 2, i + 1, i + 2, 0, i + 2] for i in range(maxJ)],
                'Qa 330': [[i + 3, 3, i, i + 3, 1, i + 3] for i in range(maxJ)],
                'Qa 331': [[i + 3, 3, i + 1, i + 3, 1, i + 2] for i in range(maxJ)],
                'Qa 440': [[i + 4, 4, i, i + 4, 2, i + 3] for i in range(maxJ)],
                'Qa 441': [[i + 4, 4, i + 1, i + 4, 2, i + 2] for i in range(maxJ)],
                'Qa JKJ-JK': [[i + 1, 1, i, i + 1, 1, i + 1] for i in range(maxJ)],
                'Qb 220': [[i + 2, 2, i, i + 2, 1, i + 1] for i in range(maxJ)],
                'Qb 221': [[i + 2, 2, i + 1, i + 2, 1, i + 2] for i in range(maxJ)],
                'Qb 330': [[i + 3, 3, i, i + 3, 2, i + 1] for i in range(maxJ)],
                'Qb 331': [[i + 3, 3, i + 1, i + 3, 2, i + 2] for i in range(maxJ)],
                'Qb 440': [[i + 4, 4, i, i + 4, 3, i + 1] for i in range(maxJ)],
                'Qb 441': [[i + 4, 4, i + 1, i + 4, 3, i + 2] for i in range(maxJ)],
                'Qc 220': [[i + 2, 2, i, i + 2, 1, i + 2] for i in range(maxJ)],
                'Qc 221': [[i + 2, 2, i + 1, i + 2, 1, i + 1] for i in range(maxJ)],
                'Qc 330': [[i + 3, 3, i, i + 3, 2, i + 2] for i in range(maxJ)],
                'Qc 331': [[i + 3, 3, i + 1, i + 3, 2, i + 1] for i in range(maxJ)],
                'Qc 440': [[i + 4, 4, i, i + 4, 3, i + 2] for i in range(maxJ)],
                'Qc 441': [[i + 4, 4, i + 1, i + 4, 3, i + 1] for i in range(maxJ)],
                'Pa 220': [[i + 2, 2, i, i + 3, 0, i + 3] for i in range(maxJ)],
                'Pa 330': [[i + 3, 3, i, i + 4, 1, i + 3] for i in range(maxJ)],
                'Pa 331': [[i + 3, 3, i + 1, i + 4, 1, i + 4] for i in range(maxJ)],
                'Pa 440': [[i + 4, 4, i, i + 5, 2, i + 3] for i in range(maxJ)],
                'Pa 441': [[i + 4, 4, i + 1, i + 5, 2, i + 4] for i in range(maxJ)],
                'Pb 220': [[i + 2, 2, i, i + 3, 1, i + 3] for i in range(maxJ)],
                'Pb 221': [[i + 2, 2, i + 1, i + 3, 1, i + 2] for i in range(maxJ)],
                'Pb 330': [[i + 3, 3, i, i + 4, 2, i + 3] for i in range(maxJ)],
                'Pb 331': [[i + 3, 3, i + 1, i + 4, 2, i + 2] for i in range(maxJ)],
                'Pb 440': [[i + 4, 4, i, i + 5, 3, i + 3] for i in range(maxJ)],
                'Pb 441': [[i + 4, 4, i + 1, i + 5, 3, i + 2] for i in range(maxJ)],
                'Pc 220': [[i + 2, 2, i, i + 3, 1, i + 2] for i in range(maxJ)],
                'Pc 221': [[i + 2, 2, i + 1, i + 3, 1, i + 3] for i in range(maxJ)],
                'Pc 330': [[i + 3, 3, i, i + 4, 2, i + 2] for i in range(maxJ)],
                'Pc 331': [[i + 3, 3, i + 1, i + 4, 2, i + 3] for i in range(maxJ)],
                'Pc 440': [[i + 4, 4, i, i + 5, 3, i + 2] for i in range(maxJ)],
                'Pc 441': [[i + 4, 4, i + 1, i + 5, 3, i + 3] for i in range(maxJ)]
                }


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
                

    
class fitfinder:
    
    def __init__(self, startwin, ratwin, derwin, prog, specwindow, fileloc = 'activememory\\'):        
        self.prog = prog
        cat = CatFile(fileloc + 'base.cat')

        with open(fileloc + 'peaklist.txt', 'r') as f:
            peaks = np.array(f.readlines(), dtype = float)
        progtranses = []
        progjkk = []
        for trans in cat.transes:
            if specwindow[0] < trans.pred < specwindow[1]:
                if trans.j1 + trans.j2 in progressions[prog]:
                    progtranses += [trans]
                    progjkk += [tuple(trans.j1 + trans.j2)]
        preds = [trans.pred for trans in progtranses]
        
        
        self.J0 = progjkk[0][0]
        self.span = progjkk[-1][0] - self.J0 + 1
        self.net = LayeredDiGraph(self.span)
        
        for jkk, pred in zip(progjkk, preds):
            for peak in peaks:
                if pred - startwin < peak:
                    if pred + startwin < peak:
                        break
                    self.net.add_node(jkk[0] - self.J0, peak, pred = pred)
        # Make initial self.network based on ratio test
        # print(len(self.net.nodes))
        for j, (layer1, layer2) in enumerate(zip(self.net.nodes[:-1], self.net.nodes[1:])):
            for obs1, dic1 in layer1.items():
                rat1 = obs1 / dic1['pred']
                for obs2, dic2 in layer2.items():
                    if abs(rat1 * dic2['pred'] - obs2) < ratwin:
                        self.net.add_edge(j, obs1, obs2)
        if not derwin:
            # Arbitrary large value
            derwin = 100
        self.dernet = LayeredDiGraph(self.span - 1)
        for j, layer1 in enumerate(self.net.nodes[:-2]):
            for obs1, dic1 in layer1.items():
                pred1 = dic1['pred']
                for obs2 in dic1['out']:
                    dic2 = self.net.nodes[j + 1][obs2]
                    pred2 = dic2['pred']
                    rat = (obs2 - obs1) / (pred2 - pred1)
                    for obs3 in dic2['out']:
                        pred3 = self.net.nodes[j + 2][obs3]['pred']
                        # print(rat * (pred3 - pred2) + obs2 - obs3)
                        if abs(rat * (pred3 - pred2) + obs2 - obs3) < derwin:
                            self.dernet.add_edge(j, (obs1, obs2), (obs2, obs3))
        # self.paths = self.pathfinder()[-1]
        # self.maxpath = len(self.paths[0])
        currnet = self.dernet
        allpaths = []
        # self.net.draw()
        for i in range(self.span - 1):
            allpaths.append([])
            for node in currnet.allnodes():
                if len(node[2]['in']) == 0 and len(node[2]['out']) == 0:
                    allpaths[-1].append(node[:2])
            # currnet.draw()
            currnet = currnet.deriv()
        # print(allpaths)
            
        allpaths = [path for path in allpaths if path]
        # print(allpaths)
        self.paths = [self.pathcleanup(*path) for path in allpaths[-1]]
            
        self.maxpath = len(self.paths[0])
    # def growpath(self, path):
    #     toret = []
    #     for segment in self.derpaths[path[-2][1]]:
    #         if segment[:2] == path[-2:]:
    #             toret += [path + (segment[-1],)]
    #     return toret
    
    # def pathfinder(self):
    #     #this only gives paths that start at lowest J
    #     allpaths = [self.derpaths[min(self.net.graph['obs'].keys())].copy()]
    #     for i in range(len(self.net.graph['obs']) - 3):
    #         allpaths += [[]]
    #         rems = []
    #         for path in allpaths[-2]:
    #             newpaths = self.growpath(path)
    #             if newpaths:
    #                 allpaths[-1] += newpaths
    #                 rems += [path]
    #         for rem in rems:
    #             allpaths[-2].remove(rem)
    #     return allpaths
        
    
    
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
    findnet = fitfinder(100, 10, 1, 'Rb J1J', (4000, 12000), 'activememory\\')
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

