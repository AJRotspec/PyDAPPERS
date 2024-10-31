This project is a reskinning of the Leopold Lab's DAPPERS program in python. We ran into issues maintaining the original LabView code, so it was deemed approrpiate to rewrite it in python, which is actually used by members of the current lab. The original code can be found at https://kleopold.chem.umn.edu/dappers.

Dependencies are tkinter, numpy, scipy, networkx, and matplotlib

The design of this is for it to run as similar to the original DAPPERS as possible. Buttons should be the same and do the same thing, more or less, as in the original, though this may change in later updates.

The dummymem folder is not required for the running of the main code, but is useful for testing purposes. Similarly, there are a few items in activememory that would normally get deleted on shutdown, but are retained for testing purposes. This can be rectified in the on_closing method of frames.py.

Current todolist:

Add in support for P branches

Fit polish

Spectral scrubber

Quartics and sextics
