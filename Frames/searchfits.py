# -*- coding: utf-8 -*-
"""
Created on Thu May  8 15:19:48 2025

@author: Aaron2
"""
from Frames.styleguide import baseframe
import os
from ratiotester import fitfinder
import time
class searchfitsframe(baseframe):
    def __init__(self, parent, row = 1, column = 1):
        root = parent.root
        frame = self.Frame(root)
        frame.grid(row = row, column = column, sticky = 'nswe', rowspan = 2)#, padx=10, pady=10)

        banner = self.Title(frame, text = 'Search for Fits')
        # banner.pack(fill="x", pady=5)  
        banner.grid(row = 0, column = 0, columnspan = 2, sticky = 'ew')
        
        labels = []
        entries = []
        for i, lab in enumerate(['Starter Window (MHz): ', 'Ratio Test Window (MHz): ', 'Derivative Ratio Test Window (MHz): ']):
            label = self.Label(frame, text = lab)
            label.grid(row = i + 1, column = 0, padx = 5, pady = 1)
            value = self.Entry(frame, width = 10)
            value.insert(0, int(100 * 10 ** -i))
            value.grid(row = i + 1, column = 1, padx = 5, pady = 1)
            labels += [label]
            entries += [value]
            
        resultsbutton = self.Button(frame, text = 'View Results')
        resultsbutton.grid(row = 4, column = 0)
        
        self.Label(frame, text = 'Max length: ').grid(row = 5, column = 0)
        maxlength = self.Label(frame, text = 'NA')
        maxlength.grid(row = 5, column = 1)
        self.Label(frame, text = 'Number of fits: ').grid(row = 6, column = 0)
        numfits = self.Label(frame, text = 'NA')
        numfits.grid(row = 6, column = 1)
        self.Label(frame, text = 'Fit search time: ').grid(row = 7, column = 0)
        fittime = self.Label(frame, text = 'NA')
        fittime.grid(row = 7, column = 1)
        def findfits():
            sttime = time.time()
            windows = [float(entry.get()) for entry in entries]
            for fil in os.listdir('activememory\\basefitbank'):
                os.remove('activememory\\basefitbank\\' + fil)
            self.ff = fitfinder(*windows, 
                                parent.proginuse.get(), 
                                (parent.freqbounddown.get(),
                                 parent.freqboundup.get()))
            fittime.configure(text = str(round(time.time() - sttime, 3)))
            
            # self.ff.writelins()
            root.setvar(name = 'rawfits', value = self.ff.paths)
            maxlength.configure(text = str(self.ff.maxpath))
            numfits.configure(text = str(len(self.ff.paths)))
            
                
        findfitsbutton = self.Button(frame, text = 'Find Fits',
                                   command = findfits)
        findfitsbutton.grid(row = 4, column = 1)
        for i in range(2):
            frame.grid_columnconfigure(i, weight=1)  
