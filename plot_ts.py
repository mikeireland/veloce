from __future__ import division, print_function
import numpy as np
import matplotlib.pyplot as plt
import csv
import datetime
from matplotlib.dates import DateFormatter
from scipy.optimize import curve_fit
from scipy.ndimage.filters import convolve
plt.ion()

def filter_times(tm_datetime, tm, temps, start=None, stop=None):
    """Utility function to filter temperature data for certain times"""
    if start is not None and stop is not None:
        ix = (tm_datetime > start) & (tm_datetime < stop)
    else:
        ix = np.ones_like(tm, dtype=bool)        
    tm_use = tm[ix]
    temps_use = temps[ix]
    tm_datetime_use = tm_datetime[ix]
    return tm_datetime_use, tm_use, temps_use

def exp_func(x, a, b, c):
    """The exponential function - NB straight out of the scipy example!"""
    return a * np.exp(-b * x) + c

def remove_exp(tm_datetime, tm, temps, start=None, stop=None):
    """Remove a fitted polynomial term from data, and return the residuals. The
    function is of the form
    T = a*exp(-b*(tm-tm_0)) + c
    
    Parameters
    ----------
    tm_datetime: numpy datetime.datetime array
        The time of the observations in datetime format.
    tm: numpy float array
        Timestamps for the data.
    temps: numpy float array
        Temperatures
    start: datetime.datetime (optional)
        The start time for fitting
    stop: datetime.datetime (optional)
        The stop time for fitting
        
    Returns
    -------
    resid: numpy arra
        Residuals to the fit.
    
    tm_datetime
    """
    tm_datetime_use, tm_use, temps_use = \
        filter_times(tm_datetime, tm, temps, start=start, stop=stop)
    p0 = [temps_use[0]-temps_use[-1], 1e-4, temps_use[-1]]
    pfit, pcov = curve_fit(exp_func, tm_use-tm_use[0], temps_use, p0=p0)
    resid = temps_use - exp_func(tm_use-tm_use[0], *pfit)
    return resid, tm_datetime_use, pfit


def remove_poly(tm_datetime, tm, temps, start=None, stop=None, deg=2):
    """Remove a fitted polynomial term from data, and return the residuals.
    
    Parameters
    ----------
    tm_datetime: numpy datetime.datetime array
        The time of the observations in datetime format.
    tm: numpy float array
        Timestamps for the data.
    temps: numpy float array
        Temperatures
    start: datetime.datetime (optional)
        The start time for fitting
    stop: datetime.datetime (optional)
        The stop time for fitting
        
    Returns
    -------
    resid: numpy float array
        Residuals to the fit.
    tm_datetime: numpy datetime.datetime array
        datetime.datetime format fo the indices
    pfit: numpy float(deg + 1) array
        Polynomial coefficients
    """
    tm_datetime_use, tm_use, temps_use = \
        filter_times(tm_datetime, tm, temps, start=start, stop=stop)
    pfit = np.polyfit(tm_use-tm_use[0], temps_use, deg)
    pfunc = np.poly1d(pfit)
    resid = temps_use - pfunc(tm_use-tm_use[0])
    return resid, tm_datetime_use, pfit

def plot_all(logfile, line='-', smooth=1):
    """Plotting function for a thermal_control log file
    
    Parameters
    ----------
    logfile: string
        Filename
    line: string
        Linestyle for plot_date
    """
    rr = csv.reader(open(logfile,'r'))
    tm = []
    t1 = []
    t2 = []
    t3 = []
    t4 = []
    for row in rr:
        if row[3].lstrip() == 'TEMPS':
            tm.append(float(row[1]))
            t1.append(float(row[4]))
            t2.append(float(row[5]))
            t3.append(float(row[6]))
            t4.append(float(row[7]))
    tm = np.array(tm)
    t1 = np.array(t1)
    t2 = np.array(t2)
    t3 = np.array(t3)
    t4 = np.array(t4)
    tm_datetime = np.array([datetime.datetime.fromtimestamp(t) for t in tm])

    #ax=plt.subplot()
    plt.clf()
    cfunc = np.ones(smooth)/float(smooth)
    plt.plot_date(tm_datetime, convolve(t1, cfunc), line, label='Table')
    plt.plot_date(tm_datetime, convolve(t2, cfunc), line, label='Lower')
    plt.plot_date(tm_datetime, convolve(t3, cfunc), line, label='Upper')
    plt.plot_date(tm_datetime, convolve(t4, cfunc), line, label='Ambient')
    #ax.xaxis.set_major_formatter( DateFormatter('%H:%M') )
    plt.ylabel("Temperature (C)")
    plt.xlabel("Date and time")
    plt.legend()
    return tm_datetime, tm, t1, t2, t3

if __name__=="__main__":
    tm_datetime, tm, t1, t2, t3 = plot_all('thermal_control.log', smooth=11)
    #tm_datetime, tm, t1, t2, t3 = plot_all('mimic_thermal.log',smooth=11)
    if (False):
        start = datetime.datetime(2017,9,1,14)
        stop = datetime.datetime(2017,9,1,15)
        resid, tm_datetime_use, pfit=remove_poly(tm_datetime, tm, t1, start=start, stop=stop, deg=3)
        plt.clf()
        plt.plot_date(tm_datetime_use, resid*1e3, '.')
        plt.ylabel('Table temp resid (mK)')
        plt.xlabel('Time')
    if (False):
        start = datetime.datetime(2017,9,2,1)
        stop = datetime.datetime(2017,9,2,9)
        start = datetime.datetime(2017,9,3,2)
        stop = datetime.datetime(2017,9,3,10)
        plt.clf()
        resid, tm_datetime_use, pfit=remove_exp(tm_datetime, tm, t1, start=start, stop=stop)
        plt.plot_date(tm_datetime_use, resid*1e3, '.', label='Table')
        print("Equilibrium Table Temperature: {:5.3f}".format(pfit[2]))
        print("Time Constant: {:8.1f} secs".format(1/pfit[1]))
        resid, tm_datetime_use, pfit=remove_exp(tm_datetime, tm, t2, start=start, stop=stop)
        plt.plot_date(tm_datetime_use, resid*1e3, '.', label='Lower')
        print("Equilibrium Lower Temperature: {:5.3f}".format(pfit[2]))
        print("Time Constant: {:8.1f} secs".format(1/pfit[1]))
        resid, tm_datetime_use, pfit=remove_exp(tm_datetime, tm, t3, start=start, stop=stop)
        plt.plot_date(tm_datetime_use, resid*1e3, '.', label='Upper')
        print("Equilibrium Upper Temperature: {:5.3f}".format(pfit[2]))
        print("Time Constant: {:8.1f} secs".format(1/pfit[1]))
        plt.ylabel('Temp resid (mK)')
        plt.xlabel('Time')
        
