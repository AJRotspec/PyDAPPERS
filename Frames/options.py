# -*- coding: utf-8 -*-
"""
Created on Thu May  8 14:24:48 2025

@author: Aaron2
"""
from Frames.styleguide import baseframe
from tkinter import filedialog, PhotoImage
from PIL import ImageTk, Image

class optionsframe(baseframe):
    def __init__(self, parent, row = 1, column = 2):
        root = parent.root
        frame = self.Frame(root)
        frame.grid(row = row, column = column, rowspan = 3, sticky = 'nsew')#, padx=10, pady=10)
        banner = self.Title(frame, text = 'Additional Options')
        banner.grid(row = 0, column = 0, columnspan = 2, sticky = 'ew')
        
        def setdefault():
            pass
        defbutton = self.Button(frame, text = 'Set Default', command = setdefault)
        defbutton.grid(row = 1, column = 0)

        def fullreset():
            pass
        resbutton = self.Button(frame, text = 'Full Reset', command = fullreset)
        resbutton.grid(row = 2, column = 0)

        def Help():
            pass
        helpbutton = self.Button(frame, text = 'Help', command = Help)
        helpbutton.grid(row = 1, column = 1)

        def setpath():
            
            defaultpath = filedialog.askdirectory(title = 'Select new default path',
                                              initialdir = root.getvar(name = 'defaultpath'))
            with open('longtermmem\\path.txt', 'w') as f:
                f.write(defaultpath)
            root.setvar(name = 'defaultpath', value = defaultpath)

        pathbutton = self.Button(frame, text = 'Set Path', command = setpath)
        pathbutton.grid(row = 2, column = 1)
        for i in range(2):
            frame.grid_columnconfigure(i, weight=1)  
        img0 = Image.open('pycomet.png')
        w, h = img0.size
        global img
        img = ImageTk.PhotoImage(img0.resize((int(w / 2), int(h / 2))))
        # img = PhotoImage(file = 'pycomet.png')
        self.Label(frame, image = img, bg = 'light grey').grid(row = 3, column = 0, columnspan = 2)

if __name__ == '__main__':
    pass
