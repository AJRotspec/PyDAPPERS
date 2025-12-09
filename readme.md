This project is a reskinning of the Leopold Lab's DAPPERS program in Python. We ran into issues maintaining the original LabView code, so it was deemed approrpiate to rewrite it in Python, which is actually used by members of the current lab. The original code can be found at https://kleopold.chem.umn.edu/dappers.

The intent of this is for it to run as similar to the original DAPPERS as possible. Buttons should be the same and do the same thing, more or less, as in the original, though there are a few additions.

A couple speedups have been incorporated, most notably in the form of the Grid Fit option. 

There are a few items in activememory that would normally get deleted on shutdown, but are retained for testing purposes. This can be rectified in the on_closing method of PyDAPPERS.py.

Current todolist:

Fit polish

Spectral scrubber

Implement cython to speed up grid fitter and peakfinding

Add in option to export peaklist
