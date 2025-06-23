# -*- coding: utf-8 -*-
"""
Created on Thu May  8 14:51:24 2025

@author: Aaron2
"""
from Frames.styleguide import baseframe
import tkinter as tk
from tkinter import Toplevel
from spfitspcat import progsT

class quantumfilterframe(baseframe):
    def __init__(self, parent, row = 3, column = 0):
        self.root = parent.root
        self.parent = parent
        frame = self.Frame(self.root)
        frame.grid(row = row, column = column, sticky = 'nswe')#, padx=10, pady=10)
        banner = self.Title(frame, text = 'Quantum Filter')
        banner.grid(row = 0, column = 0, columnspan = 4, sticky = 'ew')

        self.filterdisplay = self.Label(frame, textvariable = parent.proginuse)
        self.filterdisplay.grid(row = 1, column = 2, columnspan = 2)
    
    
        def branchselect():
            quantumfiltwindow(self)
            
 

        makebutton = self.Button(frame, text = 'Select Quantum Filter', 
                        command = branchselect)
        makebutton.grid(row = 1, column = 0, columnspan = 2)
        
        self.Label(frame, text = 'Frequency Limits (MHz):').grid(row = 2, column = 0, columnspan = 2)
        self.Label(frame, text = 'Lower').grid(row = 3, column = 0, sticky = 'e')
        self.lowerval = self.Entry(frame, textvar = parent.freqbounddown, width = 10)
        parent.freqbounddown.trace_add('write', self.updatebounds)
        self.lowerval.grid(row = 3, column = 1, sticky = 'w')
        self.Label(frame, text = 'Upper').grid(row = 4, column = 0, sticky = 'e')
        self.upperval = self.Entry(frame, textvar = parent.freqboundup, width = 10)
        parent.freqboundup.trace_add('write', self.updatebounds)
        self.upperval.grid(row = 4, column = 1, sticky = 'w')

        for i in range(2):
            frame.grid_columnconfigure(i, weight=1)  
            
        self.Label(frame, text = 'J limits:').grid(row = 2, column = 2, columnspan = 2)
        self.Label(frame, text = 'Lower').grid(row = 3, column = 2, sticky = 'e')
        self.lowerJ = self.Entry(frame, textvar = parent.Jbounddown, width = 10)
        self.lowerJ.grid(row = 3, column = 3, sticky = 'w')
        self.Label(frame, text = 'Upper').grid(row = 4, column = 2, sticky = 'e')
        self.upperJ = self.Entry(frame, textvar = parent.Jboundup, width = 10)
        self.upperJ.grid(row = 4, column = 3, sticky = 'w')
        
            
    def updatebounds(self, *args):
        lower = int(self.lowerval.get())
        upper = int(self.upperval.get())
        currprogT = progsT[self.parent.proginuse.get()]
        for i, tran in enumerate(self.parent.catlines.get()):
            # print(tran)
            # print(type(tran))
            if tran[-2] > lower:
                if tran[3] == currprogT:
                    break
        # print(tran)
        self.parent.Jbounddown.set(tran[1][0])
        for tran in self.parent.catlines.get()[i:]:
            if tran[-2] > upper:
                if tran[3] == currprogT:
                    break
        # print(tran)
        self.parent.Jboundup.set(tran[1][0])
        
        with open('longtermmem\\bounds.txt', 'w') as f:
            f.write(f'{lower}\n{upper}')

   
class quantumfiltwindow(baseframe):
    def __init__(self, parentframe):
        coldict = {'Ra': 'red', 'Rb': 'light green', 'Rc': 'blue',
                   'Qa': 'pink', 'Qb': 'cyan', 'Qc': 'purple',
                   'Pa': 'light coral', 'Pb': 'PaleGreen4', 'Pc': 'SkyBlue3'}
        progdict = {'Ra': ['J0J', 'J1J-', 'J1J+', 'J2J-', 'J2J+'],
                    'Rb': ['J1J', 'J0J', '220', '221', '330', '331'],
                    'Rc': ['110', 'J0J', '221', '220', '331', '330'],
                    'Qa': ['221', '330', '331', '440', '441', 'JKJ-JK'],
                    'Qb': ['220', '221', '330', '331', '440', '441'],
                    'Qc': ['220', '221', '330', '331', '440', '441'],
                    'Pa': ['220', '330', '331', '440', '441'],
                    'Pb': ['220', '221', '330', '331', '440', '441'],
                    'Pc': ['220', '221', '330', '331', '440', '441']}
    
        branchwindow = Toplevel(parentframe.root)
        branchwindow.title('Quantum Filters')   
    
        # Add input field and button to new window
        for i, pqr in enumerate('RQP'):
            for j, abc in enumerate('abc'):
                branch = pqr + abc
                button = self.Button(branchwindow, text = f'{pqr} Branch:\n {abc} type', width=10, height=3, bg = coldict[branch],
                                   command = lambda branch = branch: progselect(branch, branchwindow))
                button.grid(row = i, column = j, padx=10, pady=10)
        # save_button = tk.Button(input_window, text="Save", command=save)
        # save_button.pack(pady=10)
        # proginuse = tk.StringVar(master = root, value = 'hi')
        def progselect(branch, branchwindow):
            progwindow = Toplevel(parentframe.root)
            progwindow.title(f'{branch[0]} Branch {branch[1]} type')
            def save():
                for button in buttons:
                    if button[0].get():
                        parentframe.parent.proginuse.set(f'{branch} {button[1]}')
                        parentframe.updatebounds()
                progwindow.destroy()
                branchwindow.destroy()
            buttons = []
            for prog in progdict[branch]:
                togglevar = tk.BooleanVar()
                button = self.Checkbutton(progwindow, variable = togglevar, text = prog, width=10, height=3)
                buttons += [(togglevar, prog)]
                button.pack(pady = 1)
            save_button = self.Button(progwindow, text="Save", command=save)
            save_button.pack(pady=10)
