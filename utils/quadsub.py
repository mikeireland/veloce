"""Super simple script to subtract bias in each quadrant in a dodgy way"""

from __future__ import division, print_function
import numpy as np
import matplotlib.pyplot as plt
import glob
import astropy.io.fits as pyfits
import os

dir = '/Users/mireland/data/veloce/Mar01'

this_dir = os.getcwd()
os.chdir(dir)

fnames = glob.glob('T*fits')

for fn in fnames:
    im = pyfits.getdata(fn).astype(float)
    hh = pyfits.getheader(fn)
    s = im.shape
    quads = [im[0:s[0]//2,0:s[1]//2],im[s[0]:s[0]//2-1:-1,0:s[1]//2],
             im[0:s[0]//2,s[1]:s[1]//2-1:-1],im[s[0]:s[0]//2-1:-1,s[1]:s[1]//2-1:-1]]
    quads = np.array(quads, dtype='float')
    for q in quads:
        q -= np.median(q)
    im[0:s[0]//2,0:s[1]//2] = quads[0]
    im[s[0]:s[0]//2-1:-1,0:s[1]//2] = quads[1]
    im[0:s[0]//2,s[1]:s[1]//2-1:-1] = quads[2]
    im[s[0]:s[0]//2-1:-1,s[1]:s[1]//2-1:-1] = quads[3]
    pyfits.writeto('Q'+fn, im, hh, clobber=True)
    
os.chdir(this_dir)