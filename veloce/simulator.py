##Simulator code
import numpy as np
import matplotlib.pyplot as plt
#Define matrices
#Gah
gah1 = 1
gah2 = 1
gah3 = 1
gah4 = 1
gah5 = 1
gah6 = 1
#ghp
ghp1 = 1
ghp2 = 1
ghp3 = 1
ghp4 = 1
ghp5 = 1
ghp6 = 1
#Gpb
gpb1 = 1
gpb2 = 1
gpb3 = 1
gpb4 = 1
gpb5 = 1
gpb6 = 1
gpb7 = 1
#gpa
gpa1 = 1
gpa2 = 1
gpa3 = 1
gpa4 = 1
gpa5 = 1
gpa6 = 1
gpa7 = 1
#Gps
gps1 = 1
gps2 = 1
gps3 = 1
gps4 = 1
gps5 = 1
gps6 = 1
gps7 = 1
#Gsb
gsb1 = 1
gsb2 = 1
gsb3 = 1
gsb4 = 1
gsb5 = 1
gsb6 = 1
gsb7 = 1
#Gih
gih1 = 1
gih2 = 1
gih3 = 1
gih4 = 1
gih5 = 1
gih6 = 1
#gnm
g12 = 1
g13 = 1
g14 = 1
g15 = 1
g16 = 1
g17 = 1
g23 = 1
g24 = 1
g25 = 1
g26 = 1
g27 = 1
g34 = 1
g35 = 1
g36 = 1
g37 = 1
g45 = 1
g46 = 1
g47 = 1
g56 = 1
g57 = 1
g67 = 1
#ch
ch1 = 1
ch2 = 1
ch3 = 1
ch4 = 1
ch5 = 1
ch6 = 1
#cp
cp1 = 1
cp2 = 1
cp3 = 1
cp4 = 1
cp5 = 1
cp6 = 1
cp7 = 1
#cb
cb = 1
#dt_damp
dt_damp = 1
A_sim= np.array([ [-1/dt_damp, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], 
            [0, (-gpb1 - gpb2 - gpb3 - gpb4 - gpb5 - gpb6 - gpb7 - gsb2 + gsb2**2/(gps2 + gsb2) - gsb4 + gsb4**2/(gps4 + gsb4) - gsb7 + gsb7**2/(gps7 + gsb7))/cb, gpb1/cb, (gpb2 + (gps2*gsb2)/(gps2 + gsb2))/cb, gpb3/cb, (gpb4 + (gps4*gsb4)/(gps4 + gsb4))/cb, gpb5/cb, gpb6/cb, (gpb7 + (gps7*gsb7)/(gps7 + gsb7))/cb,0,0,0,0,0,0],
            [(((gah1*ghp1)/(gah1 + ghp1 + gih1) + gpa1))/cp1, (gpb1)/cp1, (-g12 - g14 - g15 - g16 - g17 - ghp1 + ghp1**2/(gah1 + ghp1 + gih1) - gpa1 - gpb1)/cp1, g12/cp1, 0, g14/cp1, g15/cp1, g16/cp1, g17/cp1, (ghp1*gih1)/(cp1*(gah1 + ghp1 + gih1)), 0, 0, 0, 0, 0],
            [((gah2*ghp2)/(gah2 + ghp2 + gih2) + gpa2)/cp2, (gpb2 + (gps2*gsb2)/(gps2 + gsb2))/cp2, g12/cp2, (-g12 - g23 - g25 - g26 - ghp2 + ghp2**2/(gah2 + ghp2 + gih2) - gpa2 - gpb2 - gps2 + gps2**2/(gps2 + gsb2))/cp2, g23/cp2, 0, g25/cp2, g26/cp2, 0, 0, (ghp2*gih2)/(cp2*(gah2 + ghp2 + gih2)), 0, 0, 0, 0],
            [((gah3*ghp3)/(gah3 + ghp3 + gih3) + gpa3)/cp3, gpb3/cp3, 0, g23/cp3, (-g23 - g34 - g35 - g36 - g37 - ghp3 + ghp3**2/(gah3 + ghp3 + gih3) - gpa3 - gpb3)/cp3, g34/cp3, g35/cp3, g36/cp3, g37/cp3, 0, 0, (ghp3*gih3)/(cp3*(gah3 + ghp3 + gih3)), 0, 0, 0],
            [((gah4*ghp4)/(gah4 + ghp4 + gih4) + gpa4)/cp4, (gpb4 + (gps4*gsb4)/(gps4 + gsb4))/cp4, g14/cp4, 0, g34/cp4, (-g14 - g34 - g45 - g46 - g47 - ghp4 + ghp4**2/(gah4 + ghp4 + gih4) - gpa4 - gpb4 - gps4 + gps4**2/(gps4 + gsb4))/cp4, g45/cp4, g46/cp4, g47/cp4, 0, 0, 0, (ghp4*gih4)/(cp4*(gah4 + ghp4 + gih4)),0,0], 
            [((gah5*ghp5)/(gah5 + ghp5 + gih5) + gpa5)/cp5, gpb5/cp5, g15/cp5, g25/cp5, g35/cp5, g45/cp5, (-g15 - g25 - g35 - g45 - g57 - ghp5 + ghp5**2/(gah5 + ghp5 + gih5) - gpa5 - gpb5)/cp5, 0, g57/cp5, 0, 0, 0, 0, (ghp5*gih5)/(cp5*(gah5 + ghp5 + gih5)), 0],
            [((gah6*ghp6)/(gah6 + ghp6 + gih6) + gpa6)/cp6, gpb6/cp6, g16/cp6, g26/cp6, g36/cp6, g46/cp6, 0, (-g16 - g26 - g36 - g46 - g67 - ghp6 + ghp6**2/(gah6 + ghp6 + gih6) - gpa6 - gpb6)/cp6, g67/cp6, 0, 0, 0, 0, 0, (ghp6*gih6)/(cp6*(gah6 + ghp6 + gih6))],
            [0, (gpb7 + (gps7*gsb7)/(gps7 + gsb7))/cp7, g17/cp7, 0, g37/cp7, g47/cp7, g57/cp7, g67/cp7, (-g17 - g37 - g47 - g57 - g67 - gpb7 - gps7 + gps7**2/(gps7 + gsb7))/cp7, 0, 0, 0, 0, 0, 0],
            [(gah1*gih1)/(ch1*(gah1 + ghp1 + gih1)), 0, (ghp1*gih1)/(ch1*(gah1 + ghp1 + gih1)), 0, 0, 0, 0, 0, 0, (-gih1 + gih1**2/(gah1 + ghp1 + gih1))/ch1, 0, 0, 0, 0, 0],
            [(gah2*gih2)/(ch2*(gah2 + ghp2 + gih2)),0, 0, (ghp2*gih2)/(ch2*(gah2 + ghp2 + gih2)), 0, 0, 0, 0, 0, 0, (-gih2 + gih2**2/(gah2 + ghp2 + gih2))/ch2, 0, 0, 0, 0],
            [(gah3*gih3)/(ch3*(gah3 + ghp3 + gih3)), 0, 0, 0, (ghp3*gih3)/(ch3*(gah3 + ghp3 + gih3)), 0, 0, 0, 0, 0, 0, (-gih3 + gih3**2/(gah3 + ghp3 + gih3))/ch3, 0, 0, 0],
            [(gah4*gih4)/(ch4*(gah4 + ghp4 + gih4)), 0, 0, 0, 0, (ghp4*gih4)/(ch4*(gah4 + ghp4 + gih4)), 0, 0, 0, 0, 0, 0, (-gih4 + gih4**2/(gah4 + ghp4 + gih4))/ch4, 0, 0],
            [(gah5*gih5)/(ch5*(gah5 + ghp5 + gih5)), 0, 0, 0, 0, 0, (ghp5*gih5)/(ch5*(gah5 + ghp5 + gih5)), 0, 0, 0, 0, 0, 0, (-gih5 + gih5**2/(gah5 + ghp5 + gih5))/ch5, 0],
            [(gah6*gih6)/(ch6*(gah6 + ghp6 + gih6)), 0, 0, 0, 0, 0, 0, (ghp6*gih6)/(ch6*(gah6 + ghp6 + gih6)), 0, 0, 0, 0, 0, 0, (-gih6 + gih6**2/(gah6 + ghp6 + gih6))/ch6] ])

B_sim = np.array([ [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0],
                   [1/ch1,0,0,0,0,0],
                   [0, 1/ch2,0,0,0,0],
                   [0,0, 1/ch3,0,0,0],
                   [0,0,0, 1/ch4,0,0],
                   [0,0,0,0, 1/ch5,0],
                   [0,0,0,0,0, 1/ch6] ])

C_sim = np.array([ [0, gsb2/(gps2 + gsb2), 0, gps2/(gps2 + gsb2), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, gsb4/(gps4 + gsb4), 0, 0, 0, gps4/(gps4 + gsb4), 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, gsb7/(gps7 + gsb7), 0, 0, 0, 0, 0, 0, gps7/(gps7 + gsb7), 0, 0, 0, 0, 0, 0] ])

#simulation variables
t_end = 1000
dt = 0.001
timesteps = round(t_end/dt)
xvalues = np.zeros( (15, timesteps) )
times = np.arange(0, timesteps*dt, dt)
#set the initial conditions
xvalues[:,0:1] = np.array([ [15],[25],[25],[25],[25],[25],[25],[25],[25],[25],[25],[25],[25],[25],[25] ]) 

yvalues = np.zeros( (3, timesteps) )

yvalues[:,0:1] = np.dot(C_sim, xvalues[:,0:1]) #calculate output at t=0
                          
u = np.zeros( (6,1) )

ambient = 15 + 2*np.sin((2*np.pi*times)/120)

#Define control loop matrices
#Gah
gah1 = 1
gah2 = 1
gah3 = 1
gah4 = 1
gah5 = 1
gah6 = 1
#ghp
ghp1 = 1
ghp2 = 1
ghp3 = 1
ghp4 = 1
ghp5 = 1
ghp6 = 1
#Gpb
gpb1 = 1
gpb2 = 1
gpb3 = 1
gpb4 = 1
gpb5 = 1
gpb6 = 1
gpb7 = 1
#gpa
gpa1 = 1
gpa2 = 1
gpa3 = 1
gpa4 = 1
gpa5 = 1
gpa6 = 1
gpa7 = 1
#Gps
gps1 = 1
gps2 = 1
gps3 = 1
gps4 = 1
gps5 = 1
gps6 = 1
gps7 = 1
#Gsb
gsb1 = 1
gsb2 = 1
gsb3 = 1
gsb4 = 1
gsb5 = 1
gsb6 = 1
gsb7 = 1
#Gih
gih1 = 1
gih2 = 1
gih3 = 1
gih4 = 1
gih5 = 1
gih6 = 1
#gnm
g12 = 1
g13 = 1
g14 = 1
g15 = 1
g16 = 1
g17 = 1
g23 = 1
g24 = 1
g25 = 1
g26 = 1
g27 = 1
g34 = 1
g35 = 1
g36 = 1
g37 = 1
g45 = 1
g46 = 1
g47 = 1
g56 = 1
g57 = 1
g67 = 1
#ch
ch1 = 1
ch2 = 1
ch3 = 1
ch4 = 1
ch5 = 1
ch6 = 1
#cp
cp1 = 1
cp2 = 1
cp3 = 1
cp4 = 1
cp5 = 1
cp6 = 1
cp7 = 1
#cb
cb = 1
#dt_damp
dt_damp = 1000
A_con= np.array([ [-1/dt_damp, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], 
            [0, (-gpb1 - gpb2 - gpb3 - gpb4 - gpb5 - gpb6 - gpb7 - gsb2 + gsb2**2/(gps2 + gsb2) - gsb4 + gsb4**2/(gps4 + gsb4) - gsb7 + gsb7**2/(gps7 + gsb7))/cb, gpb1/cb, (gpb2 + (gps2*gsb2)/(gps2 + gsb2))/cb, gpb3/cb, (gpb4 + (gps4*gsb4)/(gps4 + gsb4))/cb, gpb5/cb, gpb6/cb, (gpb7 + (gps7*gsb7)/(gps7 + gsb7))/cb,0,0,0,0,0,0],
            [(((gah1*ghp1)/(gah1 + ghp1 + gih1) + gpa1))/cp1, (gpb1)/cp1, (-g12 - g14 - g15 - g16 - g17 - ghp1 + ghp1**2/(gah1 + ghp1 + gih1) - gpa1 - gpb1)/cp1, g12/cp1, 0, g14/cp1, g15/cp1, g16/cp1, g17/cp1, (ghp1*gih1)/(cp1*(gah1 + ghp1 + gih1)), 0, 0, 0, 0, 0],
            [((gah2*ghp2)/(gah2 + ghp2 + gih2) + gpa2)/cp2, (gpb2 + (gps2*gsb2)/(gps2 + gsb2))/cp2, g12/cp2, (-g12 - g23 - g25 - g26 - ghp2 + ghp2**2/(gah2 + ghp2 + gih2) - gpa2 - gpb2 - gps2 + gps2**2/(gps2 + gsb2))/cp2, g23/cp2, 0, g25/cp2, g26/cp2, 0, 0, (ghp2*gih2)/(cp2*(gah2 + ghp2 + gih2)), 0, 0, 0, 0],
            [((gah3*ghp3)/(gah3 + ghp3 + gih3) + gpa3)/cp3, gpb3/cp3, 0, g23/cp3, (-g23 - g34 - g35 - g36 - g37 - ghp3 + ghp3**2/(gah3 + ghp3 + gih3) - gpa3 - gpb3)/cp3, g34/cp3, g35/cp3, g36/cp3, g37/cp3, 0, 0, (ghp3*gih3)/(cp3*(gah3 + ghp3 + gih3)), 0, 0, 0],
            [((gah4*ghp4)/(gah4 + ghp4 + gih4) + gpa4)/cp4, (gpb4 + (gps4*gsb4)/(gps4 + gsb4))/cp4, g14/cp4, 0, g34/cp4, (-g14 - g34 - g45 - g46 - g47 - ghp4 + ghp4**2/(gah4 + ghp4 + gih4) - gpa4 - gpb4 - gps4 + gps4**2/(gps4 + gsb4))/cp4, g45/cp4, g46/cp4, g47/cp4, 0, 0, 0, (ghp4*gih4)/(cp4*(gah4 + ghp4 + gih4)),0,0], 
            [((gah5*ghp5)/(gah5 + ghp5 + gih5) + gpa5)/cp5, gpb5/cp5, g15/cp5, g25/cp5, g35/cp5, g45/cp5, (-g15 - g25 - g35 - g45 - g57 - ghp5 + ghp5**2/(gah5 + ghp5 + gih5) - gpa5 - gpb5)/cp5, 0, g57/cp5, 0, 0, 0, 0, (ghp5*gih5)/(cp5*(gah5 + ghp5 + gih5)), 0],
            [((gah6*ghp6)/(gah6 + ghp6 + gih6) + gpa6)/cp6, gpb6/cp6, g16/cp6, g26/cp6, g36/cp6, g46/cp6, 0, (-g16 - g26 - g36 - g46 - g67 - ghp6 + ghp6**2/(gah6 + ghp6 + gih6) - gpa6 - gpb6)/cp6, g67/cp6, 0, 0, 0, 0, 0, (ghp6*gih6)/(cp6*(gah6 + ghp6 + gih6))],
            [0, (gpb7 + (gps7*gsb7)/(gps7 + gsb7))/cp7, g17/cp7, 0, g37/cp7, g47/cp7, g57/cp7, g67/cp7, (-g17 - g37 - g47 - g57 - g67 - gpb7 - gps7 + gps7**2/(gps7 + gsb7))/cp7, 0, 0, 0, 0, 0, 0],
            [(gah1*gih1)/(ch1*(gah1 + ghp1 + gih1)), 0, (ghp1*gih1)/(ch1*(gah1 + ghp1 + gih1)), 0, 0, 0, 0, 0, 0, (-gih1 + gih1**2/(gah1 + ghp1 + gih1))/ch1, 0, 0, 0, 0, 0],
            [(gah2*gih2)/(ch2*(gah2 + ghp2 + gih2)), 0, 0, (ghp2*gih2)/(ch2*(gah2 + ghp2 + gih2)), 0, 0, 0, 0, 0, 0, (-gih2 + gih2**2/(gah2 + ghp2 + gih2))/ch2, 0, 0, 0, 0],
            [(gah3*gih3)/(ch3*(gah3 + ghp3 + gih3)), 0, 0, 0, (ghp3*gih3)/(ch3*(gah3 + ghp3 + gih3)), 0, 0, 0, 0, 0, 0, (-gih3 + gih3**2/(gah3 + ghp3 + gih3))/ch3, 0, 0, 0],
            [(gah4*gih4)/(ch4*(gah4 + ghp4 + gih4)), 0, 0, 0, 0, (ghp4*gih4)/(ch4*(gah4 + ghp4 + gih4)), 0, 0, 0, 0, 0, 0, (-gih4 + gih4**2/(gah4 + ghp4 + gih4))/ch4, 0, 0],
            [(gah5*gih5)/(ch5*(gah5 + ghp5 + gih5)), 0, 0, 0, 0, 0, (ghp5*gih5)/(ch5*(gah5 + ghp5 + gih5)), 0, 0, 0, 0, 0, 0, (-gih5 + gih5**2/(gah5 + ghp5 + gih5))/ch5, 0],
            [(gah6*gih6)/(ch6*(gah6 + ghp6 + gih6)), 0, 0, 0, 0, 0, 0, (ghp6*gih6)/(ch6*(gah6 + ghp6 + gih6)), 0, 0, 0, 0, 0, 0, (-gih6 + gih6**2/(gah6 + ghp6 + gih6))/ch6] ])

B_con = np.array([ [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0], 
                   [0,0,0,0,0,0],
                   [1/ch1,0,0,0,0,0],
                   [0, 1/ch2,0,0,0,0],
                   [0,0, 1/ch3,0,0,0],
                   [0,0,0, 1/ch4,0,0],
                   [0,0,0,0, 1/ch5,0],
                   [0,0,0,0,0, 1/ch6] ])

C_con = np.array([ [0, gsb2/(gps2 + gsb2), 0, gps2/(gps2 + gsb2), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, gsb4/(gps4 + gsb4), 0, 0, 0, gps4/(gps4 + gsb4), 0, 0, 0, 0, 0, 0, 0, 0, 0],
                   [0, gsb7/(gps7 + gsb7), 0, 0, 0, 0, 0, 0, gps7/(gps7 + gsb7), 0, 0, 0, 0, 0, 0] ])
#lqg math
def main():
    for step in range(1, timesteps):
        xdot = np.dot(A_sim, xvalues[:, (step -1):step]) + np.dot(B_sim,u)
        xvalues[:,step:(step + 1)] = xvalues[:, (step - 1):step] + xdot*dt
        yvalues[:,step:(step + 1)] = np.dot(C_sim, xvalues[:, (step -1):step])
        #set ambient fluctuation
        xvalues[0,step] = ambient[step]
    plt.plot(times, yvalues[1,:])
    plt.show()