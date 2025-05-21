# -*- coding: utf-8 -*-
"""
Created on Thu May  8 14:17:37 2025

@author: Aaron2
"""
import tkinter as tk
from tkinter import filedialog, Toplevel

class baseframe:
    
    # Common functions
    @staticmethod
    def load_file(button_id, filefunc, root):
        fil = filedialog.askopenfilename(title = f'Select File for Button {button_id}',
                                         initialdir = root.getvar(name = 'defaultpath'))
        if fil:
            filefunc(fil)
                
    
    # Frames building
    @staticmethod
    def kwargsoverwriter(orig, newdefaults):
        for kwarg, item in newdefaults.items():
            orig.setdefault(kwarg, item)
        return orig
    
    maincolor = 'maroon'
    titletextcolor = 'yellow'
    titlefont = ('Helvetica', 16)
    
    titlekwargs = {'bg': maincolor,
                   'fg': titletextcolor,
                   'font': titlefont}
    
    def Title(self, *args, **kwargs):
        return tk.Label(*args, **self.kwargsoverwriter(kwargs, self.titlekwargs))
    
    labelkwargs = {}
    def Label(self, *args, **kwargs):
        return tk.Label(*args, **self.kwargsoverwriter(kwargs, self.labelkwargs))
               
    entrykwargs = {}
    def Entry(self, *args, **kwargs):
        return tk.Entry(*args, **self.kwargsoverwriter(kwargs, self.entrykwargs))
    
    
    mainfont = ('Helvetica', 14)
    
    buttonkwargs = {'bg': 'gold'}    
    def Button(self, *args, **kwargs):
        return tk.Button(*args, **self.kwargsoverwriter(kwargs, self.buttonkwargs))
    
    framekwargs = {#'borderwidth': 10,
                   # 'relief': 'solid',
                   'highlightbackground': 'black',
                   'highlightthickness': 2,
                   'bd': 1,
                   'bg': 'light gray',
                   'padx': 0,
                   'pady': 0,
                   }
    def Frame(self, *args, **kwargs):
        return tk.Frame(*args, **self.kwargsoverwriter(kwargs, self.framekwargs))
    checkbuttonkwargs = {}
    def Checkbutton(self, *args, **kwargs):
        return tk.Checkbutton(*args, **self.kwargsoverwriter(kwargs, self.checkbuttonkwargs))
    textkwargs = {}
    def Text(self, *args, **kwargs):
        return tk.Text(*args, **self.kwargsoverwriter(kwargs, self.textkwargs))


class genericwind(baseframe):
    def __init__(self, root):
        self.wind = Toplevel(root)
class txtreadwindow(baseframe):
    def __init__(self, root, filename):
        wind = Toplevel(root)
        wind.geometry('700x600')
        contents = self.Text(wind, font = ('Helvetica', 10))
        contents.pack(expand = True, fill = 'both')
        with open(filename, 'r') as f:
            contents.insert(tk.END, f.read())


