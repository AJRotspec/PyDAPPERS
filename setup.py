# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 15:34:37 2024

@author: Aaron2
"""
import os

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
    # os.mkdir('')
    
