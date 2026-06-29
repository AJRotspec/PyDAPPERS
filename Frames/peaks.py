# -*- coding: utf-8 -*-
"""
Created on Thu May  8 14:28:15 2025

@author: Aaron2
"""
from Frames.styleguide import baseframe, txtreadwindow, graphcontrols
from tkinter import Toplevel
import tkinter as tk
from spfitspcat import Spectrum
import matplotlib.pyplot as plt
import shutil
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.signal import find_peaks, savgol_filter
import numpy as np

class peaklistframe(baseframe):
    def __init__(self, parent, row = 1, column = 0):
        self.parent = parent
        root = parent.root
        frame = self.Frame(root)
        frame.grid(row = row, column = column, sticky = 'news')#, padx=60, pady=40)
        # frame.grid_propagate(False)
        banner = self.Title(frame, text = 'Experimental Peak List')
        banner.grid(row = 0, column = 0, sticky = 'we', columnspan = 2)#, padx = 50, pady=5)  
        self.Label(frame, text = 'Number of Peaks:').grid(row = 2, column = 0, padx = 10, pady = 10)
        self.Entry(frame, textvar = parent.peaknum).grid(row =2, column = 1)
        def peakfinder(fil):
            plotframe(root, fil, self)
            
        findbutton = self.Button(frame, text = 'Use Peak Finder', 
                        command = lambda: self.load_file('Use Peak Finder', peakfinder, root))
        findbutton.grid(row = 1, column = 0, padx = 10, pady = 10)
        
        def peakloader(fil):
            shutil.copy(fil, 'activememory\\peaklist.txt')
            with open('activememory\\peaklist.txt', 'r') as f:
                lines = f.readlines()
            lines.sort(key = lambda x: float(x))
            with open('activememory\\peaklist.txt', 'w') as f:
                f.writelines(lines)
                self.parent.peaknum.set(len(lines))
         
        loadbutton = self.Button(frame, text = 'Load Peak List', 
                        command = lambda: self.load_file('Load Peak List', peakloader, root))
        loadbutton.grid(row = 1, column = 1, padx = 10, pady = 10)
        
        viewbutton = self.Button(frame, text = 'View Peaklist')
        def viewpeaks():
            txtreadwindow(root, 'activememory\\peaklist.txt')
        viewbutton.configure(command = viewpeaks)
        viewbutton.grid(row = 3, column = 1, padx = 10, pady = 10)
        for i in range(2):
            frame.grid_columnconfigure(i, weight=1)  
 
class plotframe(baseframe):
    def __init__(self, root, filename, homeframe):
        plotwindow = Toplevel(root)
        plotwindow.title('Peak Picker')
        
        # Create a frame for the plot and the toolbar
        plotframe = self.Frame(plotwindow)
        plotframe.pack(side = 'left', padx=40, pady=40)

        spe = Spectrum.fromfile(filename)

        # Create the Matplotlib figure and axis
        fig, self.ax = plt.subplots(figsize = (12, 5))
        baseplot = self.ax.plot(spe.xs, spe.ys, color = 'k')
        self.ax.set_xlabel('Frequency (MHz)')

        # Embed the figure in the Tkinter window
        self.canvas = FigureCanvasTkAgg(fig, master = plotframe)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()

        pickframe = self.Frame(plotwindow)
        pickframe.pack(side = 'right', fill = tk.Y, padx=10, pady=10)

        self.Label(pickframe, text = 'Peak Picking Options').pack(pady=5)
        
        peakplot = self.ax.vlines(spe.xs[0], 0, spe.ys[0])
        baseline = savgol_filter(spe.ys, 101, 1) + 6
        baselineplot = self.ax.plot(spe.xs, baseline, color = 'b')[0]
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
            baselineplot = self.ax.plot(spe.xs, baseline, color = 'b')[0]
            self.canvas.draw()

        windowentry.bind('<Return>', adjbaseline)
        heightentry.bind('<Return>', adjbaseline)
        peaks = None
        def findpeaks():
            nonlocal peakplot, baseline, peaknumdisplay, peaks
            peakplot.remove()            
            peaks, props = find_peaks(spe.ys, height = baseline, distance = 1, width = (1, 20))         
            peakplot = self.ax.vlines(spe.xs[peaks], 0, spe.ys[peaks], color = 'r')         
            peaknumdisplay.configure(text = f'Number of peaks: {len(peaks)}')
            
            self.canvas.draw()
        graphcontrols(plotwindow, self).load()

        peaknumdisplay = self.Label(pickframe, text = 'Number of Peaks: 0')
        peaknumdisplay.pack(pady = 10)
        # Update Plot button
        findbutton = self.Button(pickframe, text = 'Find Peaks', command = findpeaks)
        findbutton.pack(pady=10)
        def close():
            dx = np.mean(np.diff(spe.xs))
            def indtox(ind):
                return spe.xs[0] + ind * dx
            y2 = np.pad(np.diff(spe.ys, 2), (1, 1))
            concs = []
            for i, (beg, mid, end) in enumerate(zip(y2[:-2], y2[1:-1], y2[2:])):
                if mid > beg and mid > end:
                    concs += [i + 1]
            nextpeak = iter(peaks)
            currpeak = next(nextpeak)
            bounds = []
            for conclow, conc in zip(concs[:-1], concs[1:]):
                try:
                    if currpeak < conc:
                        bounds.append((conclow, conc + 1))
                        currpeak = next(nextpeak)
                except:
                    break
            fits = [self.quadfit(spe.ys[bound[0]: bound[1]]) for bound in bounds]
            xpeaks = [indtox(fit[1] + bound[0]) for fit, bound in zip(fits, bounds)]

            with open('activememory\\peaklist.txt', 'w') as f:
                for peak in xpeaks:
                    f.write(f'{peak}\n')
            homeframe.parent.peaknum.set(len(peaks))
            plotwindow.destroy()
            plt.close()
        # Close button for the window
        closebutton = self.Button(pickframe, text="Close", command = close)
        closebutton.pack(pady=10)
    @staticmethod
    def quadfit(sig):
        x = np.arange(len(sig))
        X = np.array([x ** i for i in range(3)])
        coef = np.linalg.solve(X @ X.T, X @ sig)
        k = coef[2]
        x0 = -.5 * coef[1] / k
        b = coef[0] - k * x0 ** 2
        return k, x0, b
