# -*- coding: utf-8 -*-
"""
Created on Wed May 21 11:06:11 2025

@author: Aaron2
"""
from setuptools import setup
from Cython.Build import cythonize
setup(
    ext_modules = cythonize("layereddigraph.pyx")
)