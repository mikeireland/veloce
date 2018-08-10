"""Put all the LQG mathematics here so that it can be tested separately to the servo
loop"""

from __future__ import division, print_function
import numpy as np
import scipy.linalg as la

#Time interval of servo loop. As logging happens this often, we make it a moderately
#large time, but much smaller than the ~250s smallest system time constant.
lqg_dt = 2.0

#Random changes for ambient per second, tfloor, and tcryo in K.
#FIXME: this should probably automatically change when the timestep changes
T_random = 0.1*lqg_dt

#Measurement noise per second
T_noise = 0.0003*lqg_dt

#so forget that in the cost function. Mike think's that a cost function with a 
#1 in the [1,1] position is trying to minimise the RMS plate temperature. We 
#actually want the RMS sensor temperature minimised - what Q matrix would that 
#Lets only put a little weight on minimising heater current.
#FIXME: Delete this when the Q_mat below is tested.
#Q_mat = np.array([[0,0  ],
#    [0,1.0]])
    
#Better Q matrix, which needs checking
#3x3 Q
'''
Q_mat = np.array([[(G_sa**2)/((G_ps+G_sa)**2), 0, G_sa*G_ps/((G_ps+G_sa)**2)], [0, 0, 0],
                    [G_sa*G_ps/((G_ps+G_sa)**2), 0, (G_ps**2)/((G_ps+G_sa)**2)]])
'''
#2x2 Q
'''
Q_mat = np.array([[(G_sa**2)/((G_ps+G_sa)**2), G_sa*G_ps/((G_ps+G_sa)**2)],
                    [G_sa*G_ps/((G_ps+G_sa)**2), (G_ps**2)/((G_ps+G_sa)**2)]])
#Q_mat gain
'''
Q_mat = np.array([[0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0],
                  [0,0,0,0,0,0,0],
                  [0,0,0,1,0,0,0],
                  [0,0,0,0,1000,0,0],
                  [0,0,0,0,0,1,0],
                  [0,0,0,0,0,0,1]])
#To minimise the squared 
#sensor temperature, we divide by (G_sa + G_ps)**2, which is almost the same.

#2x2 model based on matlab zoh values
'''
A_mat = np.array([[0.9995,0],[3.8145e-04,0.9996]])
B_mat = np.array([[0],[0.0013]])
C_mat = np.array([[1.4998e-04,0.9999]])

'''
'''
A_mat = np.array([[0.9997,0,0], [0.0110,0.8976,0.1244], [3.0085e-04,0.0127,0.9872]])
B_mat = np.array([[0],[0.0065], [4.4184e-05]])
C_mat = np.array([[1.4998e-04,0,0.9999]])
'''

#DEFINE SIMULATION LOOP MATRIX CONSTANTS
#Side numbers 
# 1     Top/Lid
# 2     Table
# 3     Bottom/Base
# 4     Cryostat

#Heater Ambient Conductances
# The bottom has 18 heater, and the top has 42 Heaters, so define an individual heater conductance and multiply these
individual_gah = 0.0011
gah1 = individual_gah*42
gah3 = individual_gah*18
#Heater to plate conductance
#Use an individual conductance and then multiply by the number of heaters
individual_ghp = 192.6
ghp1 = individual_ghp*42
ghp3 = individual_ghp*18
ghp4 = individual_ghp
#Plate Ambient conductances, set individual conductances for these
gpa1 = 5.5206
gpa3 = 2.1756 
#Lid to base conductance
g13 = 5.046
#Lid to table radiative coupling
g12 = 3.6
#Table to Base conductance
g23 = 4.5
#Table cryostat conductance
g24 = 10
#Bottom to floor conductance
gpf3 = 3.661
#Conductance from outside of cryostat to inside temperature
gpc4 = 0.0657
#Capacitances
cp1 = 82898.64 
cp2 = 234879.48
cp3 = 46054.8  
cp4 = 8605.48

A_mat= np.array([[-0.00000000001,0,0,0,0,0,0],
                 [0,-0.00000000001,0,0,0,0,0],
                 [0,0,-0.00000000001,0,0,0,0],
                 [(gah1*ghp1 + gah1*gpa1 + ghp1*gpa1)/(cp1*(gah1 + ghp1)),0,0,((-(g12*gah1) - g13*gah1 - g12*ghp1 - g13*ghp1 - gah1*ghp1 - gah1*gpa1 - ghp1*gpa1))/(cp1*(gah1 + ghp1)),(g12*gah1 + g12*ghp1)/(cp1*(gah1 + ghp1)),(g13*gah1 + g13*ghp1)/(cp1*(gah1 + ghp1)),0],
                 [0,0,0,g12/cp2,(-g12 - g23 - g24)/cp2,g23/cp2,g24/cp2],
                 [(gah3*ghp3 + gah3*gpa3 + ghp3*gpa3)/(cp3*(gah3 + ghp3)),0,(gah3*gpf3 + ghp3*gpf3)/(cp3*(gah3 + ghp3)),(g13*gah3 + g13*ghp3)/(cp3*(gah3 + ghp3)),(g23*gah3 + g23*ghp3)/(cp3*(gah3 + ghp3)),(-(g13*gah3) - g23*gah3 - g13*ghp3 - g23*ghp3 - gah3*ghp3 - gah3*gpa3 - ghp3*gpa3 - gah3*gpf3 - ghp3*gpf3)/(cp3*(gah3 + ghp3)),0],
                 [0,gpc4/cp4,0,0,g24/cp4,0,(-g24-gpc4)/cp4]])

B_mat = np.array([[0,0,0],
                  [0,0,0],
                  [0,0,0],
                  [ghp1/(cp1*(gah1 + ghp1)),0,0],
                  [0,0,0],
                  [0,ghp3/(cp3*(gah3 + ghp3)),0],
                  [0,0,1/cp4]])
#This edited from original since we cant measure t_amb at the moment
C_mat = np.array([
                  [0,0,0,1,0,0,0],
                  [0,0,0,0,0,0,0],
                  [0,0,0,0,0,1,0],
                  [0,0,0,0,0,0,1]])
#The "R" matrix, which balances wanting small heater outputs with maintaining
#temperature.
#FIXME: This seems to bias the algorithm if heater outputs can only be 
#positive.
R_mat = 0.1*np.eye(3)





#FIXME: Not 100% certain that this is correct.
A_mat = np.eye(len(A_mat)) + lqg_dt*A_mat
           

#Scale by the timestep
B_mat *= lqg_dt

 #3x3 V
V_mat = (T_random**2)*np.eye(7)
V_mat[0,0] = T_random**2
'''
#2x2 V
V_mat = np.array([[T_random**2,0],
                          [0, 0]])
'''

W_mat = (T_noise**2)*np.eye(4) 

#Note that the first equation has a couple of matrices that have to be 
#transposed for the Riccati difference equation to apply in its standard form.
P_mat = la.solve_discrete_are(A_mat.T, C_mat.T, V_mat, W_mat)
S_mat = la.solve_discrete_are(A_mat, B_mat, Q_mat, R_mat)

#Compute the Kalman gain and Feedback gain matrices
K_mat = np.dot(np.dot(P_mat, C_mat.T), 
    np.linalg.inv(np.dot(np.dot(C_mat, P_mat), C_mat.T) + W_mat))
L_mat = np.dot(np.linalg.inv(np.dot(np.dot(B_mat.T, S_mat),B_mat)),
    np.dot(np.dot(B_mat.T, S_mat),A_mat))


#We need to store both the actual and estimated values for x
#x = np.array([[0.],[0.]])
#x_history = np.empty( (n_t, 2) )

#x_est_history = np.empty( (n_t, 2) )
#u = np.array([[0]])
#u_history = np.empty( n_t )

#Compute our estimator for x_{i+1}
#First, what do we measure at this time? This is only for simulation,
#because we actually make a measurement!
#y = np.dot(C_mat, x) 


 #Compute the actual x_i+1
#x += np.dot(A_mat, x)
#x += np.dot(B_mat, u)
#x += np.random.multivariate_normal([0,0], V_mat)

