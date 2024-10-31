# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 13:28:39 2024

@author: Aaron2
"""
import tkinter as tk
from tkinter import Toplevel
from tkinter import messagebox
from frames import *
import os
import shutil

# List to store numerical displays for each section
numerical_displays = []

# Function to open a new window for input
# def open_input_window(section):
#     def save_input():
#         # Save the input and close window
#         input_value = input_entry.get()
#         numerical_displays[section-1].config(text=f"Value: {input_value}")
#         input_window.destroy()

#     input_window = Toplevel(root)
#     input_window.title(f"Input for Section {section}")
    
#     # Add input field and button to new window
#     input_label = tk.Label(input_window, text=f"Enter value for Section {section}:")
#     input_label.pack(pady=10)
    
#     input_entry = tk.Entry(input_window)
#     input_entry.pack(pady=10)
    
#     save_button = tk.Button(input_window, text="Save", command=save_input)
#     save_button.pack(pady=10)

# Create main window
root = tk.Tk()
root.title('DAPPERS2.0')
root.configure(background='black')

peaklist = peaklistframe(root)
catfil = catfileframe(root)
quantfilt = quantumfilterframe(root)
searchfit = searchfitsframe(root)
spfit = spfitframe(root)
ops = optionsframe(root)

def on_closing():
    # if messagebox.askokcancel("Quit", "Do you want to quit?"):
    try:
        for fil in os.listdir('activememory'):
            if not os.path.isdir('activememory\\' + fil):
                os.remove('activememory\\' + fil)
    except Exception as error:
        print(error)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
