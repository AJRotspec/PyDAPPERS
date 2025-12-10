# -*- coding: utf-8 -*-
"""
Created on Thu May  8 14:17:37 2025

@author: Aaron2
"""
import tkinter as tk
from tkinter import filedialog, Toplevel
import numpy as np

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
            
class graphcontrols:
    hardxlim = (6000, 18000)
    @property
    def ax(self):
        return self.parent.ax

    def __init__(self, root, parent):
        self.root = root
        self.parent = parent
    def load(self):

        def moveleft(event):
            xlim = np.array(self.ax.get_xlim())
            xlim -= (xlim[1] - xlim[0]) * .5
            if xlim[0] < self.hardxlim[0]:
                xlim += self.hardxlim[0] - xlim[0]
            self.ax.set_xlim(*xlim)
            self.parent.canvas.draw()
        self.root.bind('a', moveleft)

        def Moveleft(event):
            xlim = np.array(self.ax.get_xlim())
            xlim -= (xlim[1] - xlim[0])
            if xlim[0] < self.hardxlim[0]:
                xlim += self.hardxlim[0] - xlim[0]
            self.ax.set_xlim(*xlim)
            self.parent.canvas.draw()
        self.root.bind('A', Moveleft)

        def moveright(event):
            xlim = np.array(self.ax.get_xlim())
            xlim += (xlim[1] - xlim[0]) * .5
            if xlim[0] > self.hardxlim[1]:
                xlim += self.hardxlim[0] - xlim[0]
            self.ax.set_xlim(*xlim)
            self.parent.canvas.draw()
        self.root.bind('s', moveright)

        def Moveright(event):
            xlim = np.array(self.ax.get_xlim())
            xlim += (xlim[1] - xlim[0])
            if xlim[0] > self.hardxlim[1]:
                xlim += self.hardxlim[0] - xlim[0]
            self.ax.set_xlim(*xlim)
            self.parent.canvas.draw()
        self.root.bind('S', Moveright)

        def zoomy(event):
            ylim = np.array(self.ax.get_ylim())
            self.ax.set_ylim(*ylim * 0.9)
            self.parent.canvas.draw()
        self.root.bind('w', zoomy)

        def Zoomy(event):
            ylim = np.array(self.ax.get_ylim())
            self.ax.set_ylim(*ylim * 0.5)
            self.parent.canvas.draw()
        self.root.bind('W', Zoomy)

        def zoomouty(event):
            ylim = np.array(self.ax.get_ylim())
            self.ax.set_ylim(*ylim * 1.1)
            self.parent.canvas.draw()
        self.root.bind('z', zoomouty)

        def Zoomouty(event):
            ylim = np.array(self.ax.get_ylim())
            self.ax.set_ylim(*ylim * 1.5)
            self.parent.canvas.draw()
        self.root.bind('Z', Zoomouty)

        def zoomx(event):
            xlim = self.ax.get_xlim()
            xspan = xlim[1] - xlim[0]
            self.ax.set_xlim(xlim[0] + xspan * 0.1, xlim[1] - xspan * 0.1)
            self.parent.canvas.draw()
        self.root.bind('e', zoomx)

        def Zoomx(event):
            xlim = self.ax.get_xlim()
            xspan = xlim[1] - xlim[0]
            self.ax.set_xlim(xlim[0] + xspan * 0.3, xlim[1] - xspan * 0.3)
            self.parent.canvas.draw()
        self.root.bind('E', Zoomx)

        def zoomoutx(event):
            xlim = self.ax.get_xlim()
            xspan = xlim[1] - xlim[0]
            self.ax.set_xlim(max(0, xlim[0] - xspan * 0.1), xlim[1] + xspan * 0.1)
            self.parent.canvas.draw()
        self.root.bind('q', zoomoutx)

        def Zoomoutx(event):
            xlim = self.ax.get_xlim()
            xspan = xlim[1] - xlim[0]
            self.ax.set_xlim(max(0, xlim[0] - xspan * 0.3), xlim[1] + xspan * 0.3)  # Zoom in by 10%
            self.parent.canvas.draw()
        self.root.bind('Q', Zoomoutx)

        def setwindow(event):
            wind = Toplevel(self.root)
            self.parent.Label(wind, text = 'Frequency Limits (MHz):').grid(row = 0, column = 0, columnspan = 2)
            self.parent.Label(wind, text = 'Frequency Limits (MHz):').grid(row = 0, column = 0, columnspan = 2)
            self.parent.Label(wind, text = 'Lower').grid(row = 1, column = 0, sticky = 'e')
            lowerval = self.parent.Entry(wind, width = 10)
            lowerval.grid(row = 1, column = 1, sticky = 'w')
            self.parent.Label(wind, text = 'Upper').grid(row = 2, column = 0, sticky = 'e')
            upperval = self.parent.Entry(wind, width = 10)
            upperval.grid(row = 2, column = 1, sticky = 'w')
            exitbutton = self.parent.Button(wind, text = 'OK')
            exitbutton.grid(row = 4, column = 0, columnspan = 2)
            def ok():
                a = float(lowerval.get())
                b = float(upperval.get())
                if a < b:
                    self.ax.set_xlim(a, b)
                    wind.destroy()
                    self.parent.canvas.draw()

            exitbutton.configure(command = ok)
        self.root.bind('f', setwindow)




