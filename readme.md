This project is a reskinning of the Leopold Lab's DAPPERS program in Python. We ran into issues maintaining the original LabView code, so it was deemed approrpiate to rewrite it in Python, which is actually used by members of the current lab. The original code can be found at https://kleopold.chem.umn.edu/dappers.

A couple speedups have been incorporated, leading to a faster fit-finding process. This has also been bundled with the option to apply coarsefit to the fits as they are generated. Taken together, these options allow a user to search with much larger windows than original DAPPERS.

The intent of this is for it to run as similar to the original DAPPERS as possible. Buttons should be the same and do the same thing, more or less, as in the original, though there are a few additions.

In order to use coarsefit, simply check the 'Apply coarsefit?' box and give it a cutoff threshold. As coarsefit is likely to overestimate the RMS of a fit by a small margin, a generous value of around 0.1 is recommended. Note that the current implementation does not work for Q branches.

There are a few items in activememory that would normally get deleted on shutdown, but are retained for testing purposes. This can be rectified in the on_closing method of PyDAPPERS.py.

There are a few features from the original version of DAPPERS that I have not yet converted into Python. These features are fit polish and the spectral scrubber. Also note that while it technically works, the peak finding is not the most precise. If you wish to use any of these functions, you are currently best off opening using them in original DAPPERS.

Please note that this code has principally been tested on molecules that I had access to during my graduate research, which had by and large a-type R branch spectra of J < 20. As such, please let me know if you run into any bugs outside these realms that I missed!

Made using
Python 3.10.5
numpy 1.26.4
matplotlib 3.10.9
scipy 1.9.0