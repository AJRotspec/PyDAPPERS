# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 10:37:20 2024

@author: Aaron2
"""

from spfitspcat import CatFile, LinFile
import numpy as np
import networkx as nx


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
                }


    
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
        
        
        self.net = nx.DiGraph(trans = {}, translist = [])
    
        for jkk, pred in zip(progjkk, preds):
            self.net.graph['trans'][jkk] = []
            self.net.graph['translist'] += [jkk]
            for peak in peaks:
                if pred - startwin < peak:
                    if pred + startwin < peak:
                        break
                    self.net.add_node((peak, jkk), pred = pred)
                    self.net.graph['trans'][jkk] += [peak]
        # Make initial self.network based on ratio test
        for tran1, tran2 in zip(self.net.graph['translist'][:-1], self.net.graph['translist'][1:]):
            for obs1 in self.net.graph['trans'][tran1]:
                for obs2 in self.net.graph['trans'][tran2]:
                    if abs(self.ratiotest(self.net.nodes[(obs1, tran1)]['pred'], obs1, self.net.nodes[(obs2, tran2)]['pred']) - obs2) < ratwin:
                        self.net.add_edge((obs1, tran1), (obs2, tran2), dercands = [])
    
        if derwin:
            # Fill out the dercands in the edges
            for tran1, tran2 in zip(self.net.graph['translist'][:-2], self.net.graph['translist'][1:-1]):
                for obs1 in self.net.graph['trans'][tran1]:
                    for obs2 in self.net.graph['trans'][tran2]:
                        for obs3, tran3 in self.net.adj[(obs2, tran2)]:
                            
                            if abs(self.deratiotest(self.net.nodes[(obs1, tran1)]['pred'], obs1, self.net.nodes[(obs2, tran2)]['pred'], obs2, self.net.nodes[(obs3, tran3)]['pred']) - obs3) < derwin:
                                self.net.edges[((obs2, tran2), (obs3, tran3))]['dercands'] += [(obs1, tran1)]
        
            # Kill edges not from level one that have no dercands
            for edge in list(self.net.edges()):
                if edge[0][1] not in self.net.graph['translist'][0]:
                    if len(self.net.edges[edge]['dercands']) == 0:
                        self.net.remove_edge(*edge)
                        
        # Kill all nodes with no edges
        for node in list(self.net.nodes):
            if self.net.degree[node] == 0:
                self.net.remove_node(node)
                self.net.graph['trans'][node[1]].remove(node[0])
        
        #This must be changed later
        self.maxpath = nx.dag_longest_path_length(self.net) + 1
        self.paths = self.pathfinder(self.maxpath - 2)
        print(nx.dag_longest_path(self.net))
        print(len(self.paths))
    
    def pathfinder(self, minlength = 4):
        subs = [self.net.subgraph(sub).copy() for sub in nx.connected_components(self.net.to_undirected())]
        maxes = [len(nx.dag_longest_path(sub)) for sub in subs]
        paths = []
        for sub in subs:
            begcaps = []
            endcaps = []
            if nx.dag_longest_path_length(sub) >= minlength:
                for node in sub.nodes:
                    if len(sub.adj[node]) == 0:
                        endcaps += [node]
                    
                for node in sub.nodes:
                    if len(sub.reverse(copy = True).adj[node]) == 0:
                        begcaps += [node]
                for begcap in begcaps:
                    for endcap in endcaps:
                        if endcap[1][0] - begcap[1][0] >= minlength:
                            paths += list(nx.all_simple_paths(sub, begcap, endcap))
        return paths
    
    def writelins(self):
        for i, path in enumerate(self.paths):
            newlin = LinFile(f'activememory\\basefitbank\\{self.prog}_{i}.lin')
            newlin.assign(path)
            newlin.makefile()
            # print(f'activememory\\basefitbank\\{self.prog}_{i}.lin')
    
    
    @staticmethod
    def ratiotest(pred1, obs1, pred2):
        return obs1 / pred1 * pred2

    @staticmethod
    def deratiotest(pred1, obs1, pred2, obs2, pred3):
        return (obs2 - obs1) * (pred3 - pred2) / (pred2 - pred1) + obs2

    def plotnet(self):
        import matplotlib.pyplot as plt
        from matplotlib import collections as mc

        nodeunpack = lambda node: (node[1][0], node[0] / self.net.nodes[node]['pred'])
        lines = [[nodeunpack(edge[0]), nodeunpack(edge[1])] for edge in self.net.edges]    
        
        fig, ax = plt.subplots()
        lc = mc.LineCollection(lines, colors = 'k')
        ax.add_collection(lc)
        plt.axis('on')
        ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
        ax.autoscale()
        ax.set_xlabel('J\"')
        ax.set_ylabel('obs / pred')
        return fig, ax, lc
        
        # fig,ax = plt.subplots()
        
        # annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
        #                     bbox=dict(boxstyle="round", fc="w"),
        #                     arrowprops=dict(arrowstyle="->"))
        # annot.set_visible(False)
        # vl = ax.vlines(freqs, 0, intens, colors = colors, gid = labels)
        # ax.hlines(0, lower, upper, color = 'k')

        # def update_annot(ind):
        #     pos = vl._paths[ind["ind"][0]].vertices[1]
        #     annot.xy = pos
        #     annot.set_text(''.join([labels[n] for n in ind['ind']]))
        
        # def hover(event):
        #     vis = annot.get_visible()
        #     if event.inaxes == ax:
        #         cont, ind = vl.contains(event)
        #         if cont:
        #             update_annot(ind)
        #             annot.set_visible(True)
        #             fig.canvas.draw_idle()
        #         else:
        #             if vis:
        #                 annot.set_visible(False)
        #                 fig.canvas.draw_idle()
        
        # fig.canvas.mpl_connect("motion_notify_event", hover)
        # plt.show()

        
if __name__ == '__main__':
    findnet = fitfinder(100, 10, 1, 'Ra J1J-', (6000, 18000))#, 'dummymem\\')
    
    # findnet.net.graph['trans'][(5, 0, 5, 4, 0, 4)]))
    # print(len(findnet.net.graph['trans'][(11, 0, 11, 10, 0, 10)]))
    fig, ax, lc = findnet.plotnet()
    rawpoints = nx.dag_longest_path(findnet.net)
    
    xs = np.array([point[1][0] for point in rawpoints])
    ys = np.array([point[0] / findnet.net.nodes[point]['pred'] for point in rawpoints])
    plt.scatter(xs, ys)
    from numpy.polynomial.polynomial import Polynomial as p
    fit = p(list(reversed(np.polyfit(xs, ys, 3))))
    print(fit)
    xfine = np.linspace(4, 11, 100)
    plt.plot(xfine, fit(xfine))

