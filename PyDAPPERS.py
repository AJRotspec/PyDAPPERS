 # -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 15:25:12 2024

@author: Aaron2
"""
import tkinter as tk
from tkinter import Toplevel, filedialog, ttk
from spfitspcat import *
from ratiotester import fitfinder, progressions
import os
import shutil
from subprocess import call, DEVNULL
from scipy.signal import find_peaks, savgol_filter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import setup
    
with open('longtermmem\\path.txt', 'r') as f:
    defaultpath = f.read()

version = '1.1'

class baseframe:
    
    # Common functions
    @staticmethod
    def load_file(button_id, filefunc):
        fil = filedialog.askopenfilename(title = f'Select File for Button {button_id}',
                                         initialdir = defaultpath)
        if fil:
            filefunc(fil)
                
    
    # Frames building
    @staticmethod
    def kwargsoverwriter(orig, newdefaults):
        for kwarg in newdefaults:
            if kwarg not in orig.keys():
                orig[kwarg] = newdefaults[kwarg]
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
    
    framekwargs = {'borderwidth': 10,
                   # 'relief': 'solid',
                   'highlightbackground': 'black',
                   'highlightthickness': 2,
                   'bd': 1,
                   'bg': 'light gray',
                   'padx': 50,
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

class fitbankbase(baseframe):
    def __init__(self, root):
        self.fitswindow = Toplevel(root)
        inputframe = self.Frame(self.fitswindow)
        inputframe.pack(side = 'left', pady = 10)
        self.labels = []
        self.entries = []
        for field in ['A', 'B', 'C']:
            
        # Add input field and button to new window
            self.labels += [self.Label(inputframe, text = f'{field} (MHz): ')]
            self.labels[-1].pack(pady=10)
            
            self.entries += [self.Entry(inputframe)]
            self.entries[-1].pack(padx=10)
            
        #putting in defaults from longtermmem
        with open('longtermmem\\abc.txt', 'r') as f:
            ABCdef = f.readlines()
        for ent, abc in zip(self.entries, ABCdef):
            ent.insert(0, abc)
            
        def quartwind():
            pass
        quarts = self.Button(inputframe, text = 'Quartic Dist', command = quartwind)
        quarts.pack(pady = 10)

        def sextwind():
            pass
        sexts = self.Button(inputframe, text = 'Sextic Dist', command = sextwind)
        sexts.pack(pady = 10)
        
        self.runbutton2 = self.Button(self.fitswindow, text = 'Run')
        self.runbutton2.pack(side = 'right')
        treeframe = self.Frame(self.fitswindow)
        treeframe.pack(side = 'left')
        self.fitdisp = ttk.Treeview(treeframe, columns = self.treeheadings, show = 'headings')
        for head in self.treeheadings:
            self.fitdisp.heading(head, text = head)
            self.fitdisp.column(head, width = 50, anchor = 'center')
        self.fitdisp.pack(side = 'right')

class txtreadwindow(baseframe):
    def __init__(self, root, filename):
        wind = Toplevel(root)
        contents = self.Text(wind)
        contents.pack(expand = True, fill = 'both')
        with open(filename, 'r') as f:
            contents.insert(tk.END, f.read())
       
class peaklistframe(baseframe):
    def __init__(self, root, row = 1, column = 0):
        frame = self.Frame(root)
        frame.grid(row = row, column = column, sticky = 'news')#, padx=60, pady=40)
        frame.grid_propagate(False)
        banner = self.Title(frame, text = 'Experimental Peak List')
        banner.pack(fill = 'x')#, padx = 50, pady=5)  
        self.peaknumdisplay = self.Label(frame, text = 'Number of Peaks: NA', font =self.mainfont)
        self.peaknumdisplay.pack(pady=10)
        
        def peakfinder(fil):
            plotframe(root, fil, self)
            
        findbutton = self.Button(frame, text = 'Use Peak Finder', 
                        command = lambda: self.load_file('Use Peak Finder', peakfinder))
        findbutton.pack(pady = 10)
        
        def peakloader(fil):
            shutil.copy(fil, 'activememory\\peaklist.txt')
            with open('activememory\\peaklist.txt', 'r') as f:
                lines = f.readlines()
            lines.sort(key = lambda x: float(x))
            with open('activememory\\peaklist.txt', 'w') as f:
                f.writelines(lines)
            self.peaknumdisplay.config(text = f'Number of Peaks: {len(lines)}')
         
        loadbutton = self.Button(frame, text = 'Load Peak List', 
                        command = lambda: self.load_file('Load Peak List', peakloader))
        loadbutton.pack(pady = 10)
        
        viewbutton = self.Button(frame, text = 'View Peaklist')
        def viewpeaks():
            txtreadwindow(root, 'activememory\\peaklist.txt')
        viewbutton.configure(command = viewpeaks)
        viewbutton.pack(pady = 10)
    
class plotframe(baseframe):
    def __init__(self, root, filename, homeframe):
        plotwindow = tk.Toplevel(root)
        plotwindow.title('Peak Picker')
        
        # Create a frame for the plot and the toolbar
        plotframe = self.Frame(plotwindow)
        plotframe.pack(side = 'left', padx=10, pady=10)

        spe = Spectrum.fromfile(filename)

        # Create the Matplotlib figure and axis
        fig, ax = plt.subplots(figsize = (12, 5))
        baseplot = ax.plot(spe.xs, spe.ys, color = 'k')
        ax.set_xlabel('Frequency (MHz)')

        # Embed the figure in the Tkinter window
        canvas = FigureCanvasTkAgg(fig, master = plotframe)
        canvas.draw()
        canvas.get_tk_widget().pack()

        pickframe = self.Frame(plotwindow)
        pickframe.pack(side = 'right', fill = tk.Y, padx=10, pady=10)

        self.Label(pickframe, text = 'Peak Picking Options').pack(pady=5)
        
        peakplot = ax.vlines(spe.xs[0], 0, spe.ys[0])
        baseline = savgol_filter(spe.ys, 101, 1) + 6
        baselineplot = ax.plot(spe.xs, baseline, color = 'b')[0]
        peakplot.set_visible(False)
        
        self.Label(pickframe, text = 'Window Size').pack(pady=5)
        windowentry = self.Entry(pickframe)
        windowentry.insert(0, '101')
        windowentry.pack(pady = 5)
        self.Label(pickframe, text = 'Baseline height').pack(pady=5)
        heightentry = self.Entry(pickframe)
        heightentry.insert(0, '6')
        heightentry.pack(pady = 5)
        
        def adjbaseline(event):
            nonlocal baseline, baselineplot
            baselineplot.remove()
            baseline = savgol_filter(spe.ys, int(windowentry.get()), 1)
            baseline += float(heightentry.get())
            baselineplot = ax.plot(spe.xs, baseline, color = 'b')[0]
            canvas.draw()

        windowentry.bind('<Return>', adjbaseline)
        heightentry.bind('<Return>', adjbaseline)
        peaks = None
        def findpeaks():
            nonlocal peakplot, baseline, peaknumdisplay, peaks
            peakplot.remove()            
            peaks, props = find_peaks(spe.ys, height = baseline, distance = 2, width = (1, 10))         
            peakplot = ax.vlines(spe.xs[peaks], 0, spe.ys[peaks], color = 'r')         
            peaknumdisplay.configure(text = f'Number of peaks: {len(peaks)}')
            
            canvas.draw()
        def moveleft(event):
            xlim = ax.get_xlim()
            xspan = xlim[1] - xlim[0]
            ax.set_xlim(xlim[0] - xspan * 0.2, xlim[1] - xspan * 0.2)
            canvas.draw()
        def Moveleft(event):
            xlim = ax.get_xlim()
            xspan = xlim[1] - xlim[0]
            ax.set_xlim(xlim[0] - xspan * 2, xlim[1] - xspan * 2)
            canvas.draw()
        def moveright(event):
            xlim = ax.get_xlim()
            xspan = xlim[1] - xlim[0]
            ax.set_xlim(xlim[0] + xspan * 0.2, xlim[1] + xspan * 0.2)
            canvas.draw()
        def Moveright(event):
            xlim = ax.get_xlim()
            xspan = xlim[1] - xlim[0]
            ax.set_xlim(xlim[0] + xspan * 2, xlim[1] + xspan * 2)
            canvas.draw()
    
        def zoomy(event):
            ylim = ax.get_ylim()
            ax.set_ylim(-5, ylim[1] * 0.9)
            canvas.draw()
        def Zoomy(event):
            ylim = ax.get_ylim()
            ax.set_ylim(-5, ylim[1] * 0.5)
            canvas.draw()
        def zoomouty(event):
            ylim = ax.get_ylim()
            ax.set_ylim(-5, ylim[1] * 1.1)
            canvas.draw()
        def Zoomouty(event):
            ylim = ax.get_ylim()
            ax.set_ylim(-5, ylim[1] * 1.5)
            canvas.draw()
        def zoomx(event):
            xlim = ax.get_xlim()
            xspan = xlim[1] - xlim[0]
            ax.set_xlim(xlim[0] + xspan * 0.1, xlim[1] - xspan * 0.1)
            canvas.draw()
        def Zoomx(event):
            xlim = ax.get_xlim()
            xspan = xlim[1] - xlim[0]
            ax.set_xlim(xlim[0] + xspan * 0.3, xlim[1] - xspan * 0.3)
            canvas.draw()
        def zoomoutx(event):
            xlim = ax.get_xlim()
            xspan = xlim[1] - xlim[0]
            ax.set_xlim(max(0, xlim[0] - xspan * 0.1), xlim[1] + xspan * 0.1)
            canvas.draw()
        def Zoomoutx(event):
            xlim = ax.get_xlim()
            xspan = xlim[1] - xlim[0]
            ax.set_xlim(max(0, xlim[0] - xspan * 0.3), xlim[1] + xspan * 0.3)  # Zoom in by 10%
            canvas.draw()

            

        # Bind keys to the Toplevel window
        plotwindow.bind('a', moveleft)
        plotwindow.bind('A', Moveleft)
        plotwindow.bind('s', moveright)
        plotwindow.bind('S', Moveright)
        plotwindow.bind('w', zoomy)
        plotwindow.bind('W', Zoomy)
        plotwindow.bind('z', zoomouty)
        plotwindow.bind('Z', Zoomouty)
        plotwindow.bind('e', zoomx)
        plotwindow.bind('E', Zoomx)
        plotwindow.bind('q', zoomoutx)
        plotwindow.bind('Q', Zoomoutx)
        peaknumdisplay = self.Label(pickframe, text = 'Number of Peaks: 0')
        peaknumdisplay.pack(pady = 10)
        # Update Plot button
        findbutton = self.Button(pickframe, text = 'Find Peaks', command = findpeaks)
        findbutton.pack(pady=10)
        def close():
            
            with open('activememory\\peaklist.txt', 'w') as f:
                for peak in spe.xs[peaks]:
                    f.write(f'{peak}\n')
            homeframe.peaknumdisplay.config(text = f'Number of Peaks: {len(peaks)}')
            plotwindow.destroy()
            
        # Close button for the window
        closebutton = self.Button(pickframe, text="Close", command = close)
        closebutton.pack(pady=10)

class catfileframe(baseframe):
    def __init__(self, root, row = 2, column = 0):
        frame = self.Frame(root)
        frame.grid(row = row, column = column, sticky = 'nswe')#, padx=10, pady=10)
        frame.grid_propagate(False)
        banner = self.Title(frame, text = 'Pickett .cat File')
        banner.pack(fill="x", pady=5)  
        def catloader(fil):
            shutil.copy(fil, 'activememory\\base.cat')
         
        loadbutton = self.Button(frame, text = 'Load Cat File', 
                        command = lambda: self.load_file('Load .cat File', catloader))
        loadbutton.pack(pady = 10)
        
    
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
        makebutton.pack(pady = 10)
        
class quantumfilterframe(baseframe):
    def __init__(self, root, row = 3, column = 0):
        frame = self.Frame(root)
        frame.grid(row = row, column = column, sticky = 'nswe')#, padx=10, pady=10)
        frame.grid_propagate(False)
        banner = self.Title(frame, text = 'Quantum Filter')
        banner.grid(row = 0, column = 0)
        self.filterdisplay = self.Label(frame, text = 'NA')
        self.filterdisplay.grid(row = 1, column = 1)
    
    
        def branchselect():
            quantumfiltwindow(root, self)
            
        def updatebounds(event):
            global upperfreq, lowerfreq
            lowerfreq = float(self.lowerval.get())
            upperfreq = float(self.upperval.get())
            with open('longtermmem\\bounds.txt', 'w') as f:
                f.write(f'{lowerfreq}\n{upperfreq}')
 

        makebutton = self.Button(frame, text = 'Select Quantum Filter', 
                        command = branchselect)
        makebutton.grid(row = 1, column = 0)
        
        self.Label(frame, text = 'Frequency Limits (MHz):').grid(row = 2, column = 0)
        global lowerfreq, upperfreq
        with open('longtermmem\\bounds.txt', 'r') as f:
            lowerfreq, upperfreq = tuple(map(float, f.readlines()))
        self.Label(frame, text = 'Lower').grid(row = 3, column = 0)
        self.lowerval = self.Entry(frame, width = 10)
        self.lowerval.grid(row = 3, column = 1)
        self.lowerval.insert(0, lowerfreq)
        self.Label(frame, text = 'Upper').grid(row = 4, column = 0)
        self.upperval = self.Entry(frame, width = 10)
        self.upperval.grid(row = 4, column = 1)
        self.upperval.insert(0, upperfreq)
        self.lowerval.bind('<Return>', updatebounds)
        self.upperval.bind('<Return>', updatebounds)

        
class quantumfiltwindow(baseframe):
    def __init__(self, root, parentframe):
        coldict = {'Ra': 'red', 'Rb': 'light green', 'Rc': 'blue',
                   'Qa': 'pink', 'Qb': 'cyan', 'Qc': 'purple',
                   'Pa': 'gray', 'Pb': 'gray', 'Pc': 'gray'}
        progdict = {'Ra': ['J0J', 'J1J-', 'J1J+', 'J2J-', 'J2J+'],
                    'Rb': ['J1J', 'J0J', '220', '221', '330', '331'],
                    'Rc': ['110', 'J0J', '221', '220', '331', '330'],
                    'Qa': ['221', '330', '331', '440', '441', 'JKJ-JK'],
                    'Qb': ['220', '221', '330', '331', '440', '441'],
                    'Qc': ['220', '221', '330', '331', '440', '441'],
                    'Pa': ['220', '330', '331', '440', '441'],
                    'Pb': ['220', '221', '330', '331', '440', '441'],
                    'Pc': ['220', '221', '330', '331', '440', '441']}
    
        branchwindow = Toplevel(root)
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
        def progselect(branch, branchwindow):
            progwindow = Toplevel(root)
            progwindow.title(f'{branch[0]} Branch {branch[1]} type')
            def save():
                for button in buttons:
                    if button[0].get():

                        parentframe.filterdisplay.config(text = f'{branch} {button[1]}')
                        global proginuse
                        proginuse = branch + ' ' + button[1]
                        
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
    
class searchfitsframe(baseframe):
    def __init__(self, root, row = 1, column = 1):
        frame = self.Frame(root)
        frame.grid(row = row, column = column, sticky = 'nswe', rowspan = 2)#, padx=10, pady=10)
        frame.grid_propagate(False)

        banner = self.Title(frame, text = 'Search for Fits')
        # banner.pack(fill="x", pady=5)  
        banner.grid(row = 0, column = 0)
        
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
        
        maxlength = self.Label(frame, text = 'Max length: NA')
        maxlength.grid(row = 5)
        
        def findfits():
            
            windows = [float(entry.get()) for entry in entries]
            ff = fitfinder(*windows, proginuse, (lowerfreq, upperfreq))
            ff.writelins()
            maxlength.configure(text = f'Max length: {ff.maxpath}')
            
                
        findfitsbutton = self.Button(frame, text = 'Find Fits',
                                   command = findfits)
        findfitsbutton.grid(row = 4, column = 1)
        
class spfitframe(baseframe):
    def __init__(self, root, row = 3, column = 1):
        frame = self.Frame(root)
        frame.grid(row = row, column = column, sticky = 'nsew')#, padx=10, pady=10)
        frame.grid_propagate(False)
        banner = self.Title(frame, text = 'Run SPFIT')
        banner.pack(fill="x", pady=5)
        
        def runfits():
            runfitswindow(root)
        runbutton = self.Button(frame, text = 'Run Fits', 
                              command = runfits)
        runbutton.pack(side = 'left', padx = 10)        

        def fitbank():
            fitbankwindow(root)
        bankbutton = self.Button(frame, text = 'Fit Bank', 
                              command = fitbank)
        bankbutton.pack(side = 'left', padx = 10)        

        def fitpolish():
            fitpolishwindow(root)
        polishbutton = self.Button(frame, text = 'Fit Polish', 
                              command = fitpolish)
        polishbutton.pack(side = 'left', padx = 10)        

class runfitswindow(fitbankbase):
    parpath = 'activememory\\fitstart.par'
    treeheadings = ('A', 'B', 'C', 'rms', 'progression', 'number of lines')

    def __init__(self, root):
        super().__init__(root)
        def run():
            values = [float(entry.get()) for entry in self.entries]
            with open('longtermmem\\abc.txt', 'w') as f:
                for val in values:
                    f.write(str(val) + '\n')
            parfil = ParVar(self.parpath, propdict = {'pars':{'10000': (values[0], 1e3, 'A'),
                                                          '20000': (values[1], 1e3, 'B'),
                                                          '30000': (values[2], 1e3, 'C')}})
            parfil.makefile()                
            fitlist = [f for f in os.listdir('activememory\\basefitbank\\') if f.endswith('lin') and proginuse in f]
            reslist = []
            for fit in fitlist:
                shutil.copy('activememory\\fitstart.par', f'activememory\\basefitbank\\{fit[:-3]}par')
                call(['Rot\\spfit', f'activememory\\basefitbank\\{fit[:-3]}par'],
                     stdout = DEVNULL, shell = True)
                os.remove(f'activememory\\basefitbank\\{fit[:-3]}par')
                os.remove(f'activememory\\basefitbank\\{fit[:-3]}bak')
                reslist += [FitFile(f'activememory\\basefitbank\\{fit[:-3]}fit')]
            reslist.sort(key = lambda x: x.rms)
            toshow = [(res.vardict['A'], res.vardict['B'], res.vardict['C'], res.rms, res.name.split('\\')[-1][:-4], len(res.assignments)) for res in reslist]
            for fit in toshow:
                self.fitdisp.insert('', 'end', values = fit)
        self.runbutton2.configure(command = run)
        
        def send():
            tosend = [self.fitdisp.item(item, "values")[4] for item in self.fitdisp.selection()]
            for item in self.fitdisp.selection():
                self.fitdisp.delete(item)                
            for fit in tosend:
                shutil.copy(f'activememory\\basefitbank\\{fit}.fit', f'activememory\\finalfitbank\\{fit}.fit')
        sendtobankbutton = self.Button(self.fitswindow, text = 'Send Selected\nFits to Fitbank', command = send)
        sendtobankbutton.pack(side = 'bottom')
        viewbutton = self.Button(self.fitswindow, text = 'View')
        viewbutton.pack(side = 'right')
        def viewfit():
            toread = self.fitdisp.item(self.fitdisp.selection()[0], "values")[4]
            txtreadwindow(root, f'activememory\\basefitbank\\{toread}.fit')
        viewbutton.configure(command = viewfit)

class fitbankwindow(fitbankbase):
    parpath = 'activememory\\finfit.par'
    treeheadings = ('ID', 'A', 'B', 'C', 'rms')
    def __init__(self, root):
        super().__init__(root)
        allfits = []
        for i, fil in enumerate(os.listdir('activememory\\finalfitbank')):
            newfit = FitFile(f'activememory\\basefitbank\\{fil}')
            toshow = (newfit.name.split('\\')[-1][:-4], newfit.vardict['A'], newfit.vardict['B'], newfit.vardict['C'], newfit.rms, i)
            self.fitdisp.insert('', 'end', values = toshow)
            allfits += [newfit]
        def comp():
            lin = LinFile('activememory\\finfit.lin')
            for item in self.fitdisp.selection():
                lin.assign(allfits[int(self.fitdisp.item(item, 'values')[-1])].assignments)
            lin.makefile()
        self.compilebutton = self.Button(self.fitswindow, text = 'Compile Selected Fits', command = comp)
        self.compilebutton.pack(side = 'bottom')
            
        self.resframe = self.Frame(self.fitswindow)
        self.resframe.pack(side = 'bottom',  fill = 'x')

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
            savepath = filedialog.askdirectory(title = f'Select new default path',
                                              initialdir = defaultpath)
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
            with open('longtermmem\\abc.txt', 'w') as f:
                for val in values:
                    f.write(str(val) + '\n')

            parfil = ParVar(self.parpath, propdict = {'pars':{'10000': (values[0], 1e3, 'A'),
                                                          '20000': (values[1], 1e3, 'B'),
                                                          '30000': (values[2], 1e3, 'C')}})
            parfil.makefile()                
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
    def __init__(self, root):
        super().__init__(root)
        self.fitdisp.destroy() 
        self.compilebutton.destroy()     
                      
class optionsframe(baseframe):
    def __init__(self, root, row = 1, column = 2):
        frame = self.Frame(root)
        frame.grid(row = row, column = column, rowspan = 3, sticky = 'nsew')#, padx=10, pady=10)
        frame.grid_propagate(False)
        banner = self.Title(frame, text = 'Additional Options')
        banner.pack(fill="x", pady=5)  
        
        def setdefault():
            pass
        defbutton = self.Button(frame, text = 'Set Default', command = setdefault)
        defbutton.pack(pady = 5)

        def fullreset():
            pass
        resbutton = self.Button(frame, text = 'Full Reset', command = fullreset)
        resbutton.pack(pady = 5)

        def Help():
            pass
        helpbutton = self.Button(frame, text = 'Help', command = Help)
        helpbutton.pack(pady = 5)

        def setpath():
            global defaultpath
            defaultpath = filedialog.askdirectory(title = f'Select new default path',
                                              initialdir = defaultpath)
            with open('longtermmem\\path.txt', 'w') as f:
                f.write(defaultpath)

        pathbutton = self.Button(frame, text = 'Set Path', command = setpath)
        pathbutton.pack(pady = 5)


root = tk.Tk()
root.title('PyDAPPERS ' + version)
root.configure(background = 'black')

for i in range(3):
    root.grid_columnconfigure(i, weight = 1)

peaklist = peaklistframe(root)
catfil = catfileframe(root)
quantfilt = quantumfilterframe(root)
searchfit = searchfitsframe(root)
spfit = spfitframe(root)
ops = optionsframe(root)



def on_closing():
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
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()


