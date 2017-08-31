from __future__ import division, print_function
import numpy as np
import matplotlib.pyplot as plt
import csv
import datetime
plt.ion()

def remove_poly(tm_datetime, tm, temps, start=None, stop=None, deg=2):
    if start is not None and stop is not None:
        ix = (tm_datetime > start) & (tm_datetime < stop)
    else:
        ix = np.ones_like(tm, dtype=bool)        
    tm_use = tm[ix]
    temps_use = temps[ix]
    tm_datetime_use = tm_datetime[ix]
    pfit = np.polyfit(tm_use-tm_use[0], temps_use, deg)
    pfunc = np.poly1d(pfit)
    resid = temps_use - pfunc(tm_use-tm_use[0])
    return resid, tm_datetime_use, pfit

def plot_all(logfile, line='-'):
    rr = csv.reader(open(logfile,'r'))
    tm = []
    t1 = []
    t2 = []
    t3 = []
    for row in rr:
        if row[3].lstrip() == 'TEMPS':
            tm.append(float(row[1]))
            t1.append(float(row[4]))
            t2.append(float(row[5]))
            t3.append(float(row[6]))
    tm = np.array(tm)
    t1 = np.array(t1)
    t2 = np.array(t2)
    t3 = np.array(t3)
    tm_datetime = np.array([datetime.datetime.fromtimestamp(t) for t in tm])

    plt.clf()
    plt.plot_date(tm_datetime, t1, line, label='Table')
    plt.plot_date(tm_datetime, t2, line, label='Lower')
    plt.plot_date(tm_datetime, t3, line, label='Upper')
    plt.ylabel("Temperature (C)")
    plt.xlabel("Date and time")
    plt.legend()
    return tm_datetime, tm, t1, t2, t3

if __name__=="__main__":
    tm_datetime, tm, t1, t2, t3 = plot_all('thermal_control.log')
    if (False):
        resid, tm_datetime_use, pfit=remove_poly(tm_datetime, tm, t1, start=datetime.datetime(2017,8,30,16), stop=datetime.datetime(2017,8,30,17), deg=3)
        plt.clf()
        plt.plot_date(tm_datetime_use, resid*1e3, '.')
        plt.ylabel('Table temp resid (mK)')
        plt.xlabel('Time')
