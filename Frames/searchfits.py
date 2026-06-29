# -*- coding: utf-8 -*-
"""
Created on Thu May  8 15:19:48 2025

@author: Aaron2
"""
from Frames.styleguide import baseframe
import os
from ratiotester import fitfinder
import time
from tkinter import BooleanVar, DoubleVar, IntVar, Toplevel
from coarsefit import progfitter
import threading

class searchfitsframe(baseframe):
    def __init__(self, parent, row = 1, column = 1):
        self.parent = parent
        root = parent.root
        self.frame = self.Frame(root)
        self.frame.grid(row = row, column = column, sticky = 'nswe', rowspan = 2)#, padx=10, pady=10)

        self.currrow = 0
        banner = self.Title(self.frame, text = 'Search for Fits')
        # banner.pack(fill="x", pady=5)  
        banner.grid(row = self.currrow, column = 0, columnspan = 2, sticky = 'ew')
        self.currrow += 1


        windowvars = []

        for i, lab in enumerate(['Starter Window (MHz): ', 'Ratio Test Window (MHz): ', 'Derivative Ratio Test Window (MHz): ']):
            self.Label(self.frame, text = lab).grid(row = self.currrow, column = 0, padx = 5, pady = 1)
            windval = IntVar(self.frame, value = int(1000 * 10 ** -i))
            self.Entry(self.frame, textvar = windval, width = 10).grid(row = self.currrow, column = 1, padx = 5, pady = 1)
            windowvars.append(windval)
            self.currrow += 1

            
        resultsbutton = self.Button(self.frame, text = 'View Results')
        resultsbutton.grid(row = self.currrow, column = 0)
        self.currrow += 1

        self.Label(self.frame, text = 'Max length: ').grid(row = 5, column = 0)
        maxlength = self.Label(self.frame, text = 'NA')
        maxlength.grid(row = self.currrow, column = 1)
        self.currrow += 1

        self.Label(self.frame, text = 'Number of fits: ').grid(row = 6, column = 0)
        numfits = self.Label(self.frame, text = 'NA')
        numfits.grid(row = self.currrow, column = 1)
        self.currrow += 1

        self.Label(self.frame, text = 'Fit search time: ').grid(row = 7, column = 0)
        fittime = self.Label(self.frame, text = 'NA')
        fittime.grid(row = self.currrow, column = 1)
        self.currrow += 1

        def findfits():
            sttime = time.time()
            windows = [float(entry.get()) for entry in windowvars]
            for fil in os.listdir('activememory\\basefitbank'):
                os.remove('activememory\\basefitbank\\' + fil)
            
            if self.usecoarsefit.get():
                coarsefitter = self.fitter
                coarsecut = self.coarsefitcutoff.get()
            else:
                coarsefitter = None
                coarsecut = None
            try:
                self.ff = fitfinder(*windows, 
                                    parent.proginuse.get(), 
                                    (parent.freqbounddown.get(),
                                    parent.freqboundup.get()),
                                    'activememory\\',
                                    coarsefitter, coarsecut)
                fittime.configure(text = str(round(time.time() - sttime, 3)))
                
                # self.ff.writelins()
                root.setvar(name = 'rawfits', value = self.ff.paths)
                maxlength.configure(text = str(self.ff.maxpath))
                numfits.configure(text = str(len(self.ff.paths)))
            except Exception as e:
                erwind = Toplevel(self.parent.root)
                self.Label(erwind, text = e).pack()
                self.Button(erwind, text = 'close', command = erwind.destroy).pack()
                
        findfitsbutton = self.Button(self.frame, text = 'Find Fits',
                                   command = findfits)
        findfitsbutton.grid(row = 4, column = 1)
        for i in range(2):
            self.frame.grid_columnconfigure(i, weight=1)
        self.incoroprate_coarsefit()


    def incoroprate_coarsefit(self):
        gridstat = self.Label(self.frame, text = 'Initializing grid')
        gridstat.grid(row = self.currrow, column = 0, columnspan= 2)
        self.currrow += 1

        def initialize_fitter():
            self.fitter = progfitter()
            gridstat.configure(text = 'Grid initialized')
        threading.Thread(target = initialize_fitter, daemon=True).start()

        self.Label(self.frame, text = 'Apply coarsefit?').grid(row = self.currrow, column = 0)
        self.usecoarsefit = BooleanVar(self.frame)
        self.Checkbutton(self.frame, variable = self.usecoarsefit).grid(row = self.currrow, column = 1)
        self.currrow += 1
        self.Label(self.frame, text = 'Coarsefit cutof?').grid(row = self.currrow, column = 0)
        self.coarsefitcutoff = DoubleVar(self.frame)
        self.Entry(self.frame, textvariable = self.coarsefitcutoff).grid(row = self.currrow, column = 1)
        self.currrow += 1
