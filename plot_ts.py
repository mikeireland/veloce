from __future__ import division, print_function
import numpy as np
import matplotlib.pyplot as plt
import csv
plt.ion()

rr = csv.reader(open('thermal_control.log','r'))
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

plt.clf()
plt.plot(tm, t1, '.', label='Table')
plt.plot(tm, t2, '.', label='Lower')
plt.plot(tm, t3, '.', label='Upper')
plt.legend()