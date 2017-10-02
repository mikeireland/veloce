from __future__ import division, print_function
import numpy as np
import matplotlib.pyplot as plt
import csv
import datetime
from matplotlib.dates import DateFormatter
from scipy.optimize import curve_fit
#thermistor eqn values, created from datasheet data

defA = 0.00113259149597421
defB = 0.000233514798680064
defC = 0.00000009045521729374

def read_in_data(logfile, line='-', smooth=1):
    #modified from Mike Irelands Plot_ts file
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
    t5 = []
    t6 = []
    t7 = []
    for row in rr:
        if row[3].lstrip() == 'Resistances':
            tm.append(float(row[1]))
            t1.append(float(row[4]))
            t2.append(float(row[5]))
            t3.append(float(row[6]))
            t4.append(float(row[7]))
            t5.append(float(row[8]))
            t6.append(float(row[9]))
            t7.append(float(row[10]))
    tm = np.array(tm)
    t1 = np.array(t1)
    t2 = np.array(t2)
    t3 = np.array(t3)
    t4 = np.array(t4)
    t5 = np.array(t5)
    t6 = np.array(t6)
    t7 = np.array(t7)
    
    tm_datetime = np.array([datetime.datetime.fromtimestamp(t) for t in tm])

    #ax=plt.subplot()
    #plt.clf()
    cfunc = np.ones(smooth)/float(smooth)
    '''
    plt.plot_date(tm_datetime, t1, line, label='Table')
    plt.plot_date(tm_datetime, t2, line, label='Lower')
    plt.plot_date(tm_datetime, t3, line, label='Upper')
    plt.plot_date(tm_datetime, t4, line, label='Ambient')
    plt.plot_date(tm_datetime, t5, line, label='Aux 1')
    plt.plot_date(tm_datetime, t6, line, label='Aux 2')
    plt.plot_date(tm_datetime, t7, line, label='Aux 3')
    '''
    #ax.xaxis.set_major_formatter( DateFormatter('%H:%M') )
    #plt.ylabel("Temperature (C)")
    #plt.xlabel("Date and time")
    #plt.legend()
    #plt.show()
    return t1, t2, t4, t5, t6, t7
    
def thermistor_eqn(resistance, A, B, C):
    aVal = A
    bVal = B
    cVal = C
    temp_inv = aVal + bVal*np.log(resistance) + cVal*((np.log(resistance))**3)
    tempKelv = 1/(temp_inv)
    tempCelc = tempKelv -273.15
    return tempCelc

def calibrate():
    #first read in data
    data = read_in_data('logfile.log')
    #Now lets use channel 1 as a reference and calulate temperature values for that based defaultthermistor constants
    temp_ch_1 = np.zeros(len(data[0]))
    for i, res in enumerate(data[0]):
        temp_ch_1[i] = thermistor_eqn(res, defA, defB, defC)
    # now we can use sciy curve_fit for the other eqn's using temp_ch_1 as the ydata
    pvals = np.zeros((3,7))
    for i in range(1,6):
        print(i)
        popt, pcov = curve_fit(thermistor_eqn, data[i], temp_ch_1, (defA, defB, defC))
        pvals[:,i] = popt
    temp_ch_x = np.zeros((7,len(data[1])))
    temp_ch_x[0,:] = temp_ch_1
    for y in range(1,7):
        print(y)
        for i, res in enumerate(data[1]):
            temp_ch_x[y,i] = thermistor_eqn(res, pvals[0,y], pvals[1,y], pvals[2,y])
    import pdb; pdb.set_trace()
    return popt, pcov