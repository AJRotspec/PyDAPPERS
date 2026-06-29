# -*- coding: utf-8 -*-
"""
Created on Thu May  8 15:23:14 2025

@author: Aaron2
"""
from Frames.styleguide import baseframe, txtreadwindow, genericwind
from spfitspcat import FitFile, IntFile, LinFile
import tkinter as tk
from tkinter import filedialog, Toplevel, ttk
from spfitspcat import ParVar
import os
import shutil
from subprocess import call, DEVNULL
from coarsefit import progfitter
import threading

import time

class spfitframe(baseframe):
    def __init__(self, parent, row = 3, column = 1):
        root = parent.root
        frame = self.Frame(root)
        frame.grid(row = row, column = column, sticky = 'nsew')#, padx=10, pady=10)
        frame.grid_propagate(False)
        self.Title(frame, text = 'Run SPFIT').grid(row = 0, column = 0, columnspan = 3, sticky = 'ew')
        
        # gridstat = self.Label(frame, text = 'Initializing grid')
        # gridstat.grid(row = 2, column = 1, columnspan= 2)
        # def initialize_fitter():
        #     self.fitter = progfitter()
        #     gridstat.configure(text = 'Grid initialized')
        # threading.Thread(target = initialize_fitter, daemon=True).start()
        
        def runfits():
            runfitswindow(root, self)
        runbutton = self.Button(frame, text = 'Run Fits', 
                              command = runfits)
        runbutton.grid(row = 1, column = 0)    

        def fitbank():
            fitbankwindow(root, self)
        self.Button(frame, text = 'Fit Bank', command = fitbank).grid(row = 1, column = 1)     

        def fitpolish():
            fitpolishwindow(root, self)
        # self.Button(frame, text = 'Fit Polish', command = fitpolish).grid(row = 1, column = 2)
        for i in range(3):
            frame.grid_columnconfigure(i, weight=1)  
        # def gridfit():
        #     gridfitwindow(root, self)
        # self.Button(frame, text = 'Grid Fit', command = gridfit).grid(row = 2, column = 0)



class distwind(baseframe):
    def __init__(self, root, parent):
        self.window = Toplevel(root)
        self.window.title('Distortion Constants')
        self.Label(self.window, text = 'Constant').grid(row = 0, column = 0)
        self.Label(self.window, text = 'Value').grid(row = 0, column = 1)
        self.Label(self.window, text = 'Include').grid(row = 0, column = 2)
        self.Label(self.window, text = 'Fix').grid(row = 0, column = 3)

        self.entries = []
        self.onoffs = []
        self.fixes = []
        self.toggles = {}
        for i, param in enumerate(self.params):
            self.Label(self.window, text = param).grid(row = i + 1, column = 0)
            self.entries += [self.Entry(self.window)]
            self.entries[-1].grid(row = i + 1, column = 1)
            self.entries[-1].insert(0, '0.0')
            use = tk.BooleanVar()
            self.onoffs += [self.Checkbutton(self.window, variable = use)]
            self.onoffs[-1].grid(row = i + 1, column = 2)
            fix = tk.BooleanVar()
            self.fixes += [self.Checkbutton(self.window, variable = fix)]
            self.fixes[-1].grid(row = i + 1, column = 3)
            self.toggles[param] = (use, fix)
        self.apply = self.Button(self.window, text = 'Apply')
        self.apply.grid(row = i + 2, column = 0, columnspan = 2)
        self.cancel = self.Button(self.window, text = 'Cancel')
        self.cancel.grid(row = i + 2, column = 2, columnspan = 2)
        def applyfunc():
            usedict = {key: list(map(lambda x: x.get(), item)) for key, item in self.toggles.items()}
            for param, entry, code in zip(self.params, self.entries, self.codes):
                usedict[param] += [float(entry.get()), code]
            parent.dists.update(usedict)
            self.window.destroy()    
        self.apply.configure(command = applyfunc)
        def cancelfunc():
            self.window.destroy()            
        self.cancel.configure(command = cancelfunc)


class fitbankbase(baseframe):
    def __init__(self, root, parent):
        self.fitswindow = Toplevel(root)
        self.dists = {}
        self.inputframe = self.Frame(self.fitswindow)
        self.inputframe.grid(row = 0, column = 0, rowspan = 2)
        self.labels = []
        self.entries = []
        self.Label(self.inputframe, text = 'Constant').grid(row = 0, column = 0)
        self.Label(self.inputframe, text = 'Value').grid(row = 0, column = 1)
        self.Label(self.inputframe, text = 'Fix').grid(row = 0, column = 2)
        self.fixes = []
        self.toggles = []
        for i, field in enumerate(['A', 'B', 'C']):
            
        # Add input field and button to new window
            self.labels += [self.Label(self.inputframe, text = f'{field} (MHz): ')]
            self.labels[-1].grid(row = i + 1, column = 0, pady = 15)
            
            self.entries += [self.Entry(self.inputframe)]
            self.entries[-1].grid(row = i + 1, column = 1)
            fix = tk.BooleanVar()
            self.fixes += [self.Checkbutton(self.inputframe, variable = fix)]
            self.fixes[-1].grid(row = i + 1, column = 3)
            self.toggles += [fix]
            
        #putting in defaults from longtermmem
        with open('longtermmem\\abc.txt', 'r') as f:
            ABCdef = f.readlines()
        for ent, abc in zip(self.entries, ABCdef):
            ent.insert(0, abc)

        def quarts():
            class quartwind(distwind):
                params = ['DeltaJ', 'DeltaJK', 'DeltaK', 'deltaJ', 'deltaK']
                codes = ['200', '1100', '2000', '40100', '41000']
            quartwind(root, self)
            
        quarts = self.Button(self.inputframe, text = 'Quartic Dist', command = quarts)
        quarts.grid(row = 5, column = 0, columnspan = 3, pady = 15)

        def sextwind():
            pass
        sexts = self.Button(self.inputframe, text = 'Sextic Dist', command = sextwind)
        sexts.grid(row = 6, column = 0, columnspan = 3)
        self.bottomframe = self.Frame(self.fitswindow)
        self.bottomframe.grid(row = 1, column = 1)
        
        self.runbutton2 = self.Button(self.bottomframe, text = 'Run')
        self.runbutton2.pack(side = 'left')
        self.treeframe = self.Frame(self.fitswindow)
        self.treeframe.grid(row = 0, column = 1, sticky = 'ew')
        self.fitdisp = ttk.Treeview(self.treeframe, columns = self.treeheadings, show = 'headings')
        for head in self.treeheadings:
            self.fitdisp.heading(head, text = head)
            self.fitdisp.column(head, width = 50, anchor = 'center')
        self.fitdisp.pack(fill = 'x')


class runfitswindow(fitbankbase):
    parpath = 'activememory\\fitstart.par'
    treeheadings = ('A', 'B', 'C', 'rms', 'progression', 'number of lines')

    def __init__(self, root, parent):
        super().__init__(root, parent)
        def run():
            values = [float(entry.get()) for entry in self.entries]
            uncs = [1e-3 if fix.get() else 1e3 for fix in self.toggles]            
            # fixes = 

            with open('longtermmem\\abc.txt', 'w') as f:
                for val in values:
                    f.write(str(val) + '\n')
            self.parfil = ParVar(self.parpath, propdict = {'pars':{'10000': (values[0], uncs[0], 'A'),
                                                          '20000': (values[1], uncs[1], 'B'),
                                                          '30000': (values[2], uncs[2], 'C')}})
            
            for dist, items in self.dists.items():
                if items[0]:
                    if items[1]:
                        unc = 1e-3
                    else:
                        unc = 1e3
                    self.parfil.pars[items[3]] = (-items[2], unc, '-' + dist)
                
            self.parfil.makefile()     
            proginuse = root.getvar(name = 'proginuse')
            # rawfits = root.getvar(name = 'rawfits')
            # for i, fit in enumerate(rawfits):
            #     newlin = LinFile(f'activememory\\basefitbank\\{proginuse}_{i}.lin')
            #     newlin.assign([(pair[1], pair[0]) for pair in fit])
            #     newlin.makefile()
            fitlist = [f for f in os.listdir('activememory\\basefitbank\\') if f.endswith('lin') and proginuse in f]

            reslist = []
            
            def fittores(fitfile):
                return (fitfile.vardict['A'], fitfile.vardict['B'], fitfile.vardict['C'], fitfile.rms, fitfile.name.split('\\')[-1][:-4], fitfile.assignments)
            
            for fit in fitlist:
                shutil.copy('activememory\\fitstart.par', f'activememory\\basefitbank\\{fit[:-3]}par')
                
                call(['Rot\\spfit', f'activememory\\basefitbank\\{fit[:-3]}par'],
                     stdout = DEVNULL, shell = True)
                os.remove(f'activememory\\basefitbank\\{fit[:-3]}par')
                os.remove(f'activememory\\basefitbank\\{fit[:-3]}bak')
                reslist += [FitFile(f'activememory\\basefitbank\\{fit[:-3]}fit')]
            reslist.sort(key = lambda x: x.rms)
            allfits = [fittores(res) for res in reslist]
            for fit in allfits:
                self.fitdisp.insert('', 'end', values = fit[:-1] + (len(fit[-1]),))

        self.runbutton2.configure(command = run)
                        
        def send():
            tosend = [self.fitdisp.item(item, "values")[4] for item in self.fitdisp.selection()]
            for item in self.fitdisp.selection():
                self.fitdisp.delete(item)                
            for fit in tosend:
                shutil.copy(f'activememory\\basefitbank\\{fit}.fit', f'activememory\\finalfitbank\\{fit}.fit')

        sendtobankbutton = self.Button(self.bottomframe, text = 'Send Selected\nFits to Fitbank', command = send)
        sendtobankbutton.pack(side = 'right')
        viewbutton = self.Button(self.bottomframe, text = 'View')
        viewbutton.pack(side = 'right')
        def viewfit():
            toread = self.fitdisp.item(self.fitdisp.selection()[0], "values")[4]
            txtreadwindow(root, f'activememory\\basefitbank\\{toread}.fit')
        viewbutton.configure(command = viewfit)
        
        

class fitbankwindow(fitbankbase):
    parpath = 'activememory\\finfit.par'
    treeheadings = ('ID', 'A', 'B', 'C', 'rms')
    def __init__(self, root, parent):
        super().__init__(root, parent)
        allfits = []
        for i, fil in enumerate(os.listdir('activememory\\finalfitbank')):
            newfit = FitFile(f'activememory\\finalfitbank\\{fil}')
            toshow = (newfit.name.split('\\')[-1][:-4], newfit.vardict['A'], newfit.vardict['B'], newfit.vardict['C'], newfit.rms, i)
            self.fitdisp.insert('', 'end', values = toshow)
            allfits += [newfit]
        def comp():
            lin = LinFile('activememory\\finfit.lin')
            for item in self.fitdisp.selection():
                lin.assign(allfits[int(self.fitdisp.item(item, 'values')[-1])].assignments)
            lin.makefile()
        self.compilebutton = self.Button(self.bottomframe, text = 'Compile Selected Fits', command = comp)
        self.compilebutton.pack(side = 'bottom')
            
        self.resframe = self.Frame(self.fitswindow)
        self.resframe.grid(row = 1, column = 2)
        self.treeframe.grid_configure(columnspan = 2)
        

        finrms = self.Label(self.resframe, text = 'rms: ')
        finrms.pack(side = 'left', padx = 10)

        finA = self.Label(self.resframe, text = 'A: ')
        finA.pack(side = 'left', padx = 10)

        finB = self.Label(self.resframe, text = 'B: ')
        finB.pack(side = 'left', padx = 10)

        finC = self.Label(self.resframe, text = 'C: ')
        finC.pack(side = 'left', padx = 10)
        
        
        makecatbutton = self.Button(self.resframe, text = 'Make .cat File')
        makecatbutton.pack(side = 'right')
        def makecat():
            def save():
                values = [float(entry.get()) for entry in entries]
                intfil = IntFile(self.parpath[:-3] + 'int', values)
                intfil.makefile()
                call(['Rot\\spcat', self.parpath[:-3] + 'var'],
                     stdout = DEVNULL, shell = True)
                input_window.destroy()

            if 'base.int' in os.listdir('activememory'):
                shutil.copy('activememory\\base.int', self.parpath[:-3] + 'int')
            else:
                input_window = Toplevel(root)
                input_window.title('Input Dipole Moments')
                labels = []
                entries = []
                for field in ['µa', 'µb', 'µc']:
                    labels += [self.Label(input_window, text = f'{field}: ')]
                    labels[-1].pack(pady=10)
                    
                    entries += [self.Entry(input_window)]
                    entries[-1].pack(padx=10)
                self.Button(input_window, text = 'Save', command = save).pack(pady = 10)
        makecatbutton.configure(command = makecat)
        savebutton = self.Button(self.resframe, text = 'Save')
        savebutton.pack(side = 'right')
        def save():
            savepath = filedialog.askdirectory(title = 'Select new default path',
                                              initialdir = root.getvar(name = 'defaultpath'))
            basenamewindow = Toplevel(root)
            self.Label(basenamewindow, text = 'Input base name').pack(pady = 5)
            basename = self.Entry(basenamewindow)
            basename.pack(pady = 10)
            def finsave(event):
                for ext in ['fit', 'lin', 'par', 'var', 'int', 'cat']:
                    try:
                        shutil.copy(self.parpath[:-3] + ext, savepath + '/' + basename.get() + '.' + ext)
                    except:
                        pass
                basenamewindow.destroy()

            basename.bind('<Return>', finsave)
        savebutton.configure(command = save)
        
        def run():
            values = [float(entry.get()) for entry in self.entries]
            uncs = [1e-3 if fix.get() else 1e3 for fix in self.toggles]            

            with open('longtermmem\\abc.txt', 'w') as f:
                for val in values:
                    f.write(str(val) + '\n')
            
            self.parfil = ParVar(self.parpath, propdict = {'pars':{'10000': (values[0], uncs[0], 'A'),
                                                          '20000': (values[1], uncs[1], 'B'),
                                                          '30000': (values[2], uncs[2], 'C')}})
            for dist, items in self.dists.items():
                if items[0]:
                    if items[1]:
                        unc = 1e-3
                    else:
                        unc = 1e3
                    self.parfil.pars[items[3]] = (-items[2], unc, '-' + dist)

            self.parfil.makefile()                
            call(['Rot\\spfit', self.parpath],
                 stdout = DEVNULL, shell = True)
            os.remove(self.parpath[:-3] + 'bak')
            finfit = FitFile(self.parpath[:-3] + 'fit')
            finrms.configure(text = f'rms: {finfit.rms}')
            finA.configure(text = f'A: {finfit.vardict["A"]}')
            finB.configure(text = f'B: {finfit.vardict["B"]}')
            finC.configure(text = f'C: {finfit.vardict["C"]}')
            
        self.runbutton2.configure(command = run)
        viewbutton = self.Button(self.resframe, text = 'View')
        viewbutton.pack(side = 'right')
        def viewfit():
            txtreadwindow(root, self.parpath[:-3] + 'fit')
        viewbutton.configure(command = viewfit)

class fitpolishwindow(fitbankwindow):
    parpath = 'activememory\\polishfit.par'
    def __init__(self, root, parent):
        super().__init__(root)
        self.fitdisp.destroy() 
        self.compilebutton.destroy()     

