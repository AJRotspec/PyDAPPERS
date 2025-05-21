# -*- coding: utf-8 -*-
"""
Created on Thu May  8 14:49:34 2025

@author: Aaron2
"""
from Frames.styleguide import baseframe
from tkinter import Toplevel
from spfitspcat import ParVar, IntFile, CatFile
import shutil
class catfileframe(baseframe):
    def __init__(self, parent, row = 2, column = 0):
        root = parent.root
        frame = self.Frame(root)
        frame.grid(row = row, column = column, sticky = 'nswe')#, padx=10, pady=10)
        banner = self.Title(frame, text = 'Pickett .cat File')
        banner.grid(row = 0, column = 0, sticky = 'ew', columnspan = 2)#, padx = 50, pady=5)  
        def catloader(fil):
            shutil.copy(fil, 'activememory\\base.cat')
         
        loadbutton = self.Button(frame, text = 'Load Cat File', 
                        command = lambda: self.load_file('Load .cat File', catloader, root))
        loadbutton.grid(row = 1, column = 0)
        
    
        def catmaker():
            def save():
                values = [float(entry.get()) for entry in entries]
                with open('longtermmem\\abc.txt', 'w') as f:
                    for val in values[:3]:
                        f.write(str(val) + '\n')

                varfil = ParVar('activememory\\base.var', propdict = {'pars':{'10000': (values[0], 1, 'A'),
                                                              '20000': (values[1], 1, 'B'),
                                                              '30000': (values[2], 1, 'C')}})
                varfil.makefile()
                intfil = IntFile('activememory\\base.int', values[3:])
                intfil.makefile()
                varfil.makecat()
                newcat = CatFile('activememory\\base.cat')
                parent.catlines.set(value = newcat.transes)
                input_window.destroy()
    
    
            input_window = Toplevel(root)
            input_window.title('Generate .cat File')
            labels = []
            entries = []
            with open('longtermmem\\abc.txt', 'r') as f:
                defaults = f.readlines()

            defaults += ['1', '1', '1']
            for field, default in zip(['A', 'B', 'C', 'µa', 'µb', 'µc'], defaults):
                
            # Add input field and button to new window
                labels += [self.Label(input_window, text = f'{field}: ')]
                labels[-1].pack(pady=10)
                
                entries += [self.Entry(input_window)]
                entries[-1].insert(0, default)
                entries[-1].pack(padx=10)
            
            save_button = self.Button(input_window, text="Save", command=save)
            save_button.pack(pady=10)
    
         
        makebutton = self.Button(frame, text = 'Generate .cat File', 
                        command = catmaker)
        # makebutton = tk.Button(frame, text = 'Generate .cat File', 
        #                 command = lambda: input_window(root, 'Generate .cat File', ['A', 'B', 'C', 'µa', 'µb', 'µc'], catmakersave), **self.buttonkwargs)
        makebutton.grid(row = 1, column = 1)
        for i in range(2):
            frame.grid_columnconfigure(i, weight=1)  
