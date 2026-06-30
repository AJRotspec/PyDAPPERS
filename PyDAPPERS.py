 # -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 15:25:12 2024

@author: Aaron2
"""
import tkinter as tk
# from Frames import *
from Frames.styleguide import genericwind
from Frames.options import optionsframe
from Frames.peaks import peaklistframe
from Frames.catfile import catfileframe
from Frames.filters import quantumfilterframe
from Frames.searchfits import searchfitsframe
from Frames.spfit import spfitframe

from spfitspcat import CatFile
import os

version = '2.0'

"""

Basic workflow is that the user selects a collection of peaks,
either via the peak finder or by loading a list in the peaks frame.
These peaks are written into activememory/peaklist.txt

The user then either loads or generates a .cat file using the catfile
frame. This is stored as activememory/base.cat

A progression is then selected from the filters frame. It's stored in
the proginuse StringVar. This window also allows for the selection of
the frequency limits, which determine the expected range of the 
transitions. All of these are stored in the freqbound and Jbound tkVars.

The user then navigates to the searchfits frame, where they may set
the tolerances for the core DAPPERS algorithm. New to this method, they
also decide if and at what tolerance to apply gridfit. More info can
be found in those files, but potential fits are recorded as .lin files
in activememory/basefitbank/

The spfit frame has three buttons, intended to be used from left to right
    Run Fits calls spfit on all the .lin files generated in the last step.
    The user will see them sorted by rms, may view the full .fit files, 
    and send selected fits to the fitbank by highlighting and pressing the
    'send selected fits to fitbank' button. This writes them into the 
    activememory/finalfitbank/ directory.

    Fit Bank is intended to be used once multiple sets of lines from several
    progressions have been sent to the fit bank. In this window, the user
    can mix and match the subsets together in order to create a final 
    version of the fit

    When finished, Fit Polish allows the user to finalize a fit.


"""


# Do setup

                      

class mainwindow():
    filepaths = [
        'activememory\\basefitbank',
        'activememory\\finalfitbank',
        'longtermmem'
    ]
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('PyDAPPERS ' + version)
        self.root.configure(background = 'black')

        self.check_filetree()
        # Define all 'global' variables
        self.initialize_globals()

        
        # initialize all frames
        self.peaklist = peaklistframe(self)
        self.catfil = catfileframe(self)
        self.quantfilt = quantumfilterframe(self)
        self.searchfit = searchfitsframe(self)
        self.spfit = spfitframe(self)
        self.ops = optionsframe(self)
       
     
        def on_closing():
            closewind = genericwind(self.root)
            # if self.spfit.gridthread:
            #     pass
            #     # self.spfit.gridstopevent.set()
            #     # self.spfit.gridthread.join()
            closewind.Label(closewind.wind, text = 'Retain active memory? (Not recommended)').pack()
            def killactive():
                try:
                    
                #     for fil in os.listdir('activememory'):
                #         if not os.path.isdir('activememory\\' + fil):
                #             os.remove('activememory\\' + fil)
                    for fil in os.listdir('activememory\\basefitbank'):
                        if not os.path.isdir('activememory\\basefitbank\\' + fil):
                            os.remove('activememory\\basefitbank\\' + fil)
                    for fil in os.listdir('activememory\\finalfitbank'):
                        if not os.path.isdir('activememory\\finalfitbank\\' + fil):
                            os.remove('activememory\\finalfitbank\\' + fil)
                except Exception as error:
                    print(error)
                self.root.destroy()
            # def keepactive():
            #     self.root.destroy()
            # closewind.Button(closewind.wind, text = 'Keep active memory', command = keepactive).pack()
            # closewind.Button(closewind.wind, text = 'Delete active memory', command = killactive).pack()

            killactive()
        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        
        self.root.mainloop()

    def check_filetree(self):
        for path in self.filepaths:
            os.makedirs(path, exist_ok = True)
        if not 'path.txt' in os.listdir('longtermmem'):
            with open('longtermmem\\path.txt', 'w') as f:
                f.write('C:/')
            
        if not 'abc.txt' in os.listdir('longtermmem'):            
            with open('longtermmem\\abc.txt', 'w') as f:
                f.write('30000\n2000\n1000')

        if not 'bounds.txt' in os.listdir('longtermmem'):
            with open('longtermmem\\bounds.txt', 'w') as f:
                f.write('6000\n18000')

        if not 'peaklist.txt' in os.listdir('activememory'):
            with open('activememory\\peaklist.txt', 'w') as f:
                f.write('\n')


    def initialize_globals(self):
        with open('longtermmem\\path.txt', 'r') as f:
            defaultpath = f.read()
        self.defaultpath = tk.StringVar(self.root, name = 'defaultpath', value = defaultpath)
        
        with open('activememory\\peaklist.txt', 'r') as f:
            peaknum = len(f.readlines())
        self.peaknum = tk.IntVar(self.root, name = 'peaknum', value = peaknum)
        
        with open('longtermmem\\bounds.txt', 'r') as f:
            lower, upper = tuple(map(int, f.readlines()))
        self.freqboundup = tk.IntVar(self.root, name = 'freqboundup', value = upper)
        self.freqbounddown = tk.IntVar(self.root, name = 'freqbounddown', value = lower)
        self.Jboundup = tk.IntVar(self.root, name = 'Jboundup', value = 0)
        self.Jbounddown = tk.IntVar(self.root, name = 'Jbounddown', value = 0)

        self.proginuse = tk.StringVar(self.root, name = 'proginuse', value = 'None selected')
        
        tempcat = CatFile('activememory\\base.cat')
        self.catlines = tk.Variable(self.root, name = 'catlines', value = tempcat.transes)
        self.rawfits = tk.Variable(self.root, name = 'rawfits')
        self.fitbankfits = tk.Variable(self.root, name = 'fitbankfits', value = [])


mainwindow()  
