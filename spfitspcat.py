# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 08:51:22 2022

@author: Aaron2
"""

from scipy.signal import find_peaks, savgol_filter
import numpy as np
#import matplotlib.pyplot as plt
import os
import shutil
from subprocess import call, DEVNULL

class Spectrum:

    noisewindow = 30
    peakwindow = 100
    xstep = 0.03999982222301234
    datnum = 75000
    scrubs = None
    
    def __init__(self, name, xs, ys, avs = 1, peaklist = False, scrubs = False):
        self.name = name
        self.xs = np.asarray(xs)
        #self.ys = np.array(savgol_filter(ys, 7, 3))
        self.ys = np.asarray(ys)
        self.ys -= np.median(self.ys)
        
        lowerx = min(self.xs)
        if scrubs:
            for scrub in scrubs:
                # bot, top = [Spectrum.find_nearest(xs, scrub[i]) for i in range(2)]
                bot, top = [int((scrub[i] - lowerx) / Spectrum.xstep) for i in range(2)]
                self.ys[bot:top] = 0
        # self.ys=np.array(savgol_filter(self.ys,5,3))
        if len(ys) != Spectrum.datnum:
            self.datnum = len(ys)
                
        self.range = f"{round(0.001 * min(xs))}–{round(0.001 * max(xs))}"
        self.noise = np.median([np.abs(y) for y in self.ys])
        self.ys /= self.noise
        self.peaks = []
        self.avs = avs
        self.peakprops = None


    @classmethod
    def fromfile(cls, filename):
        if filename[-3:] == 'spe':
            return cls.fromspe(filename)
        elif filename[-3:] == 'csv':
            return cls.fromcsv(filename)
    @classmethod
    def fromspe(cls, filename, peaklist = False, scrubs = False):
        with open(filename, 'r') as f:       
            xs, ys = np.array([line.split() for line in f.readlines()], dtype = float).T
        return Spectrum(filename, xs, ys, 1, peaklist, scrubs)
    
    @classmethod
    def fromcsv(cls, filename):
        with open(filename, 'r') as f:       
            xs, ys = np.array([line.split(',') for line in f.readlines()[1:]], dtype = float).T
        return Spectrum(filename[:-3] + 'spe', xs, ys)

    
    def findpeaks(self, repick = False):
        if f"{self.name.replace('.spe', '')}_spfitspcat_peakx.txt" in os.listdir():
            if repick:
                return
            else:
                #unpack the data from file
                pass
        self.peakinds, self.peakprops = find_peaks(self.ys, height = self.noise * 8,
                                              prominence = self.noise / 2,
                                              threshold = self.noise,
                                              distance = 20)
        self.peaks = [[self.xs[ind], height] for ind, height
                      in zip(self.peakinds, self.peakprops['peak_heights'])]
        

    def averager(self, newspec):
        if newspec.avs == 0:
            return Spectrum(self.name, newspec.xs, newspec.ys, newspec.avs)
        avdys = []
        newtot = self.avs + newspec.avs
        for yold, ynew in zip(self.ys, newspec.ys):
            avdys += [(yold * self.avs + ynew * newspec.avs) / newtot]
        self.ys =  np.array(avdys)
        self.avs = newtot
        
    def makefile(self):
        with open(self.name, 'w') as f:
            for x, y in zip(self.xs, self.ys):
                f.write("{:.11f}".format(x) + '\t' + "{:.11f}".format(y) + '\n')
                
    def HyperFilter(self, window):
        ranges = [[]]
        for peak, npeak in zip(self.peaks[:-1], self.peaks[1:]):
            ranges[-1] += [peak]
            if npeak[0] > peak[0] + window:

                ranges += [[]]
                
        if self.peaks[-1][0] > ranges[-1][-1][0] + window:
            ranges += [[]]
        ranges[-1] += [self.peaks[-1]]

        maxer = lambda x: sorted(x, key = lambda y: y[1])[-1][0]
        return [maxer(x) for x in ranges]
         
    def copy(self):
        return Spectrum(self.name, self.xs, self.ys, self.avs, self.peaklist)
           

    @staticmethod
    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return idx

class Transition:
    HF = False
    states = False
    catlines = False
    maxJ = 30
    progressions = {'aJ0J':[[i + 1, 0 , i + 1, i, 0, i] for i in range(maxJ)],
                    'aJ1J-':[[i + 1, 1 , i + 1, i, 1, i] for i in range(maxJ)],
                    'aJ1J+':[[i + 2, 1 , i + 1, i + 1, 1, i] for i in range(maxJ)],
                    'aJ2J-':[[i + 2, 2 , i + 1, i + 1, 2, i] for i in range(maxJ)],
                    'aJ2J+':[[i + 3, 2 , i + 2, i + 2, 2, i] for i in range(maxJ)],
                    'bJ1J': [[i + 1, 1 , i + 1, i, 0, i] for i in range(maxJ)],
                    'bJ0J': [[i + 1, 0 , i + 1, i, 1, i] for i in range(maxJ)],
                    'b220': [[i + 2, 2 , i, i + 1, 1, i + 1] for i in range(maxJ)],
                    'b221': [[i + 2, 2 , i + 1, i + 1, 1, i] for i in range(maxJ)],
                    'c110': [[i + 1, 1 , i, i, 0, i] for i in range(maxJ)],
                    'cJ0J': [[i + 2, 0 , i + 2, i + 1, 1, i] for i in range(maxJ)],
                    'c221': [[i + 2, 2 , i + 1, i + 1, 1, i + 1] for i in range(maxJ)],
                    'c220': [[i + 2, 2 , i, i + 1, 1, i] for i in range(maxJ)]}
    
    def __init__(self, j1, j2, catargs = False):
        self.j1 = j1
        self.j2 = j2
        self.J = j1[0]
        
        if len(j1)  == 5:
            self.HF = True
            self.States = True
        
        linname = ''
        for j in self.j1: linname += "{:3}".format(j)
        for j in self.j2: linname += "{:3}".format(j)
        linname += '  0' * 6
        self.linname = linname
        
        
        if catargs:
            for arg in catargs.keys():
                self.__dict__[arg] = catargs[arg]
        else:
            catname = self.linname.replace('  ', ' ')
            self.catname = ''
            for j in self.j1:
                self.catname += '{:2d}'.format(j)
            self.catname += 6 * ' '
            for j in self.j2:
                self.catname += '{:2d}'.format(j)
            
            # self.catname = catname[:6] + 6 * ' ' + catname[6:12]
            self.inten = None
            self.pred = None
            if Transition.catlines:
                for line in Transition.catlines:
                    if self.catname in line:
                        self.pred, _,  self.inten, *_ = line.split()
                        self.pred = float(self.pred)
                        self.inten = float(self.inten)
                        break
        #self.prog = Transition.proglabel(self.j1, self.j2)
        
        self.prog = None
        tolookup = self.j1[:3] + self.j2[:3]
        for prog, progs in Transition.progressions.items():
            if tolookup in progs:
                self.prog = prog 
        
    def __repr__(self):
        return self.linname
       
    def next_in_series(self, updown):
        #updown = + or - 1
        if updown == -1 and self.j2[2] == 0:
            return None
        if updown == +1 and self.j1[0] == Transition.maxJ:
            return None
        transs = Transition.progressions[self.prog]
        for i, trans in enumerate(transs):
            if trans[0] == self.J:
                ind = i
        newj1 = transs[ind + updown][:3]
        newj2 = transs[ind + updown][3:]
        if Transition.HF:
            newj1 += [self.j1[3] + updown]
            newj2 += [self.j2[3] + updown]
        return Transition(newj1, newj2)
    
    @classmethod
    def fromlinname(cls, linname):
        linnums = linname.split()
        splitind = 3
        if cls.HF:
            splitind += 1
        j1 = list(map(int, linnums[:splitind]))
        j2 = list(map(int, linnums[splitind:]))
        return Transition(j1, j2)
        
    @classmethod
    def fromcatline(cls, catline):
        tomake = {}
        tomake['name'] = catline[55:]
        #transition indices are 55-56, 57-58, 59-60, 67-68, 69-70, 71-72
        #If HF there are also 61-62 and 73-
        #For HF and states, we have 55-65 and 67-78 split into pairs 
        try:
            j1 = [int(catline[j:j + 2]) for j in range(55, 60, 2)]
            j2 = [int(catline[j:j + 2]) for j in range(67, 72, 2)]
        except: print(catline)
        if catline[62] in [str(i) for i in range(10)]:
            j1 += [int(catline[61:63])]
            j2 += [int(catline[73:75])]
     
        tomake['pred'] = float(catline[3:13])
        tomake['inten'] = float(catline[22:28])
        return Transition(j1, j2, tomake)


class ParVar:
    def __init__(self, filename, towrites = None, propdict = None):
        self.filename = filename
        self.basename = filename[:-4]
        self.parvar = filename[-4:]
        if propdict:
            for arg in propdict.keys():
                self.__dict__[arg] = propdict[arg]
            self.idlines = 'test                                                  Wed Oct 23 14:31:43 2024\n\
   8  101   30    0    0.0000E+000    1.0000E+023    1.0000E+000 1.0000000000\n\
     a     1     1     0    40     0     1     1     1     0     0\n'

        else:
            with open(filename, 'r') as f:
                lines = f.readlines()
            self.idlines = lines[:3]
            parlines = []
            self.noninc = []
            for i, line in enumerate(lines[3:]):
                if line == '\n':
                    self.noninc = lines[i + 3:]
                    break
                parlines += [line]
            self.pars = {}
            for line in parlines[:i]:
                name, *rawprops = line.split()
                print(rawprops)
                #rawprops is a tuple of the form (val, unc, comments)
                props = [float(rawprops[0]), float(rawprops[1]),
                         ''.join(x if x != '/' else '' for x in rawprops[2:])]
                self.pars[name] = props
    
    def makefile(self, name = None):
        if not name:
            name = self.basename + self.parvar
            #if self.parvar == '.var' and f"{self.basename}.int" in os.listdir():
            #    shutil.copy(f"{self.basename}.int", f"{name[:-3]}int")
        with open(name, 'w') as f:
            f.writelines(self.idlines)
            for par in self.pars.keys():
                val, unc, com = self.pars[par]
                f.write(par.rjust(13))
                val = f" {val: .15E}"
                unc = f"{unc: .8E}"
                for cha in ['+', '-']:
                    val = val.replace(f'E{cha}', f'E{cha}0')
                    unc = unc.replace(f'E{cha}', f'E{cha}0')
                f.write(f"{val}{unc} /{com}\n")
            try:
                f.writelines(self.noninc)
            except:
                pass
        
    def fromprops(self, basename, propdict):
        pass
        
    def makecat(self):
        call(['Rot\\spcat', os.path.join(os.getcwd(), self.basename + self.parvar)],
             stdout = DEVNULL, shell = True)
        return f"{self.basename}.cat"

class IntFile:
    def __init__(self, filename, dipole):
        self.name = filename
        self.dipole = dipole
    def makefile(self):
        #Make the int file
        with open(f"{self.name}", 'w') as f:
            f.write(f"{self.name}\n")
            f.write('0   1    0        0  40   -10.0   -10.0    40  5\n')
            
            for i, dip, xyz in zip('123', self.dipole, 'xyz'):
                f.write(f"\t{i} {float(dip): .4f} / {xyz} dipole moment\n")


class CatFile:
    mintensity = -1
    
    def __init__(self, filename):
        self.filename = filename
        self.transes = []
        with open(filename, 'r') as f:
            for line in f.readlines():
                self.transes += [Transition.fromcatline(line)]
        self.transes.sort(key = lambda x: x.pred)
        
    def points(self, a, b):
        xs = []
        ys = []
        for tran in self.transes:
            if tran.pred > a:
                if tran.pred > b:
                    break
                if tran.inten > self.mintensity:
                    xs += [tran.pred]
                    ys += [10 ** tran.inten]
            
        return xs, ys


class LinFile:
    def __init__(self, filename):
        self.name = filename
        self.lines = []
    
    def assign(self, assignmentpairs):
        # assignmentpairs is a list of 2-tuples of type
        # (obs, (tuple of transition jkk))
        for pair in assignmentpairs:
            self.lines += [{'obs': pair[0], 'jkk': pair[1]}]
    def makefile(self):
        self.lines.sort(key = lambda x: x['obs'])
        with open(self.name, 'w') as f:
            for line in self.lines:
                for j in line['jkk']:
                    f.write(str(j).rjust(3))
                f.write('  0  0  0  0  0  0   ')
                f.write(f'{np.round(line["obs"], 3)}'.rjust(9))
                f.write('    0.01500   1.0000\n')

class FitFile:
    def __init__(self, filename):
        self.name = filename
        with open(filename, 'r') as f:
            lines = f.readlines()
        lines.reverse()
        codedict = {'A': ' 10000 ', 'B': ' 20000 ', 'C': ' 30000 '}
        self.vardict = {}
        self.assignments = []
        for line in lines:
            if 'MICROWAVE RMS' in line:
                self.rms = round(float(line.split()[3]), 3)
            for key, item in codedict.items():
                if item in line:
                    self.vardict[key] = float(line.split()[3].split('(')[0])
            if 'EXP.FREQ.' in line:
                break
            if ': ' in line and 'Diverging' in line:
                words = line.split()
                jkk = words[1:7]
                obs = float(words[7])
                self.assignments += [(obs, jkk)]
        self.assignments.sort()
        
        
        
            
if __name__ == '__main__':
    # values = [5, 4, 3, 1, 1, 1]
    # varfil = ParVar('activememory\\base.var', propdict = {'pars':{'10000': (values[0], 1, 'A'),
    #                                              '20000': (values[1], 1, 'B'),
    #                                              '30000': (values[2], 1, 'C')}})
    # varfil.makefile()
    # intfil = IntFile('activememory\\base.int', values[3:])
    # intfil.makefile()
    # varfil.makecat()
    l = LinFile('a.lin')
    l.assign([(10075.36999, (6, 0, 6, 5, 0, 5)), (6088.1234, (4, 0, 4, 3, 0, 3))])
    l.makefile()


