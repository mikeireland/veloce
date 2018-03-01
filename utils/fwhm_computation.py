from __future__ import division, print_function
import numpy as np
import matplotlib.pyplot as plt
import glob
import astropy.io.fits as pyfits
import scipy.ndimage as nd
from astropy.modeling import models, fitting
plt.ion()

fnames = glob.glob('/Users/mireland/data/veloce/Feb28/QE*fits')
focus = [int(f[-8:-5]) for f in fnames]

fnames = glob.glob('/Users/mireland/data/veloce/Feb28/Qe*fits')
focus = np.zeros( (len(fnames)) )

fnames = glob.glob('/Users/mireland/data/veloce/Mar01/QT*fits')
focus = [int(f[-8:-5]) for f in fnames]

nstart=8
nfirst=3
threshold=500
display_it=False
x_ignore = 100 #500 for etalon data.
#------------------------------------------

szx = pyfits.getheader(fnames[0])['NAXIS1']
szy = pyfits.getheader(fnames[0])['NAXIS2']

#First lets read in the first few frames, and take a median to search for 
#bright lines. We do this to avoid cosmic rays.
first_data = np.zeros((nfirst,szy,szx))
for ix, fn in enumerate(fnames[nstart:nstart+nfirst]):
        first_data[ix] = pyfits.getdata(fn)
med_data = np.median(first_data, axis=0)

#Now lets look for possible peaks amongst the difference between this median
#frame and a smoothed version of it.
smoothim = nd.median_filter(med_data,(3,3))
wpeaks = np.where(med_data-smoothim > threshold)

#Lets manually make sure we only pick each peak once by just using the first coordinate
#we find within 5 pixels.
peaks = []
nfound = 0
for xix, yix in zip(wpeaks[1], wpeaks[0]):
    if xix<x_ignore or yix <100 or xix>4100 or yix>4000:
        continue
    surrounding_pix = med_data[yix-5:yix+5,xix-5:xix+5]
    if np.max(surrounding_pix) > 40000:
        continue
    duplicate=False
    for p in peaks:
        dpeak = np.sqrt( (p[0]-xix)**2 + (p[1]-yix)**2 )
        if dpeak < 12:
            duplicate=True
            continue
    if not duplicate:
        peaks.append([int(xix),int(yix)])
        nfound += 1
        if (nfound % 100 == 0):
            print("Done {:d} peaks".format(nfound))
peaks = np.array(peaks)

#Now lets run through the images and fit a 2D Gaussian in the vicinity of each peak.
peakparams = np.zeros( (len(fnames),peaks.shape[0], 6) )
hw = 5
fit_p = fitting.LevMarLSQFitter()
xy_fit = np.meshgrid(np.arange(2*hw), np.arange(2*hw))
for j, fn in enumerate(fnames):
    print("Doing file {:d} of {:d}".format(j, len(fnames)))
    dd = pyfits.getdata(fn)
    for i, xyix in enumerate(peaks):
        subarr = dd[xyix[1]-hw:xyix[1]+hw, xyix[0]-hw:xyix[0]+hw]
        subarr -= np.median(subarr)
        if (False):
            plt.clf()
            plt.imshow(subarr)
            plt.pause(0.001)
        xymax = np.argmax(subarr)
        xymax = np.unravel_index(xymax, subarr.shape)
        p_init = models.Gaussian2D(amplitude=np.max(subarr),x_mean=xymax[1], y_mean=xymax[0], 
            x_stddev = 3.0, y_stddev = 3.0, fixed={"theta":True})
        p = fit_p(p_init, xy_fit[0], xy_fit[1], subarr)
        peakparams[j,i] = [p.amplitude.value, p.x_mean.value, p.y_mean.value, p.x_stddev.value, p.y_stddev.value, p.theta.value]
        if ((peakparams[j,i,4]<1.5/2.35) and (i != 2) and display_it==True):
            print(focus[j])
            print(xyix)
            print(p)
            plt.clf()
            plt.imshow(subarr)
            plt.plot(peakparams[j,i,1], peakparams[j,i,2], 'x')
            plt.pause(.001)
            #import pdb; pdb.set_trace()

focus = np.array(focus)
if np.max(np.abs(focus)) > 0:
    wfoc = np.where((focus > 150) & (focus < 180))[0]

    spectral_best = np.mean(peakparams[wfoc,:,4], axis=0)
    
spat_ix=-3 #-3 for best. Also 9
for j in np.arange(0,2):
    plt.figure(j+1)
    plt.clf()
    if j==0:
        wc = np.where( (peaks[:,1]>500) * (peaks[:,1] < 3500))[0]
    else:
        wc = np.where( (peaks[:,0]>500) * (peaks[:,0] < 3500))[0]
    plt.plot(peaks[wc,j], peakparams[spat_ix,wc,3]*2.35,'.', label='Spatial')
    plt.plot(peaks[wc,j], peakparams[spat_ix,wc,4]*2.35,'.', label='Spectral')
    plt.axis([100,4000,0,2.5])
    plt.legend()
    plt.ylabel('FWHM')
    if j==0:
        plt.xlabel('y pix')
    else:
        plt.xlabel('x pix')
    