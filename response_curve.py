import astropy.io.fits as pyfits
import numpy as np
import matplotlib.pyplot as plt
plt.ion

fn = 'Rosso002.fits'
xs = [385, 537, 684, 830, 970, 1109, 1240, 1372, 1496, 1622, 1742, 1855, 1971, 2081,\
    2191, 2296, 2397, 2501, 2597, 2697, 2788, 2876, 2965, 3050,\
    3140, 3218, 3299, 3380, 3454, 3528, 3603, 3676, \
    3744, 3813, 3882, 3944, 4005, 4068]
#-----------
dd = pyfits.getdata(fn)
#subtract overscan
dd = dd[:dd.shape[0]//2,:].astype(float)
dd[:,:dd.shape[1]//2] -= np.median(dd[:,:20])
dd[:,dd.shape[1]//2:] -= np.median(dd[:,-20:])


profile = np.sum(dd[-50:,:], axis=0)

#Rough wavelengths
orders = 66 + np.arange(len(xs))
wave = 31600*2*np.sin(np.radians(75.4))/orders

fluxes = np.zeros(len(xs))
for i in range(len(xs)):
    fluxes[i] = np.sum(profile[xs[i]-10:xs[i]+10])
    
plt.plot(wave, fluxes)