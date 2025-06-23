 # -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 15:25:12 2024

@author: Aaron2
"""
import tkinter as tk
# from Frames import *
# from Frames.styleguide import genericwind
from Frames.options import optionsframe
from Frames.peaks import peaklistframe
from Frames.catfile import catfileframe
from Frames.filters import quantumfilterframe
from Frames.searchfits import searchfitsframe
from Frames.spfit import spfitframe

from spfitspcat import CatFile
import os

version = '2.0'

# Do setup
if not 'longtermmem' in os.listdir():
    os.mkdir('longtermmem')
    with open('longtermmem\\path.txt', 'w') as f:
        f.write('C:/')
    with open('longtermmem\\abc.txt', 'w') as f:
        f.write('30000\n2000\n1000')
    with open('longtermmem\\bounds.txt', 'w') as f:
        f.write('6000\n18000')
    os.mkdir('activememory')
    os.mkdir('activememory\\basefitbank')
    os.mkdir('activememory\\finalfitbank')

                      

class mainwindow():
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('PyDAPPERS ' + version)
        self.root.configure(background = 'black')
        
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
            # closewind = genericwind(self.root)
            
            # closewind.Label(closewind.wind, text = 'Retain active memory? (Not recommended)').pack()
            def killactive():
                try:
                    
                    for fil in os.listdir('activememory'):
                        if not os.path.isdir('activememory\\' + fil):
                            os.remove('activememory\\' + fil)
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

    def initialize_globals(self):
        with open('longtermmem\\path.txt', 'r') as f:
            defaultpath = f.read()
        self.defaultpath = tk.StringVar(self.root, name = 'defaultpath', value = defaultpath)
        with open('longtermmem\\bounds.txt', 'r') as f:
            lower, upper = tuple(map(int, f.readlines()))
        self.freqboundup = tk.IntVar(self.root, name = 'freqboundup', value = upper)
        self.freqbounddown = tk.IntVar(self.root, name = 'freqbounddown', value = lower)
        self.Jboundup = tk.IntVar(self.root, name = 'Jboundup', value = 0)
        self.Jbounddown = tk.IntVar(self.root, name = 'Jbounddown', value = 0)

        self.proginuse = tk.StringVar(self.root, name = 'proginuse', value = 'Rb J1J')
        
        tempcat = CatFile('activememory\\base.cat')
        self.catlines = tk.Variable(self.root, name = 'catlines', value = tempcat.transes)
        self.rawfits = tk.Variable(self.root, name = 'rawfits')
        self.fitbankfits = tk.Variable(self.root, name = 'fitbankfits', value = [])


mainwindow()  
