"""
This single thermal plate simulator needs documentation!

What is the 
"""

from __future__ import print_function, division
import numpy as np
import matplotlib.pyplot as plt
import scipy.linalg as la

#Define thermal conductivities. Units: Watts/K.
G_sa = 1.0
G_ah = 1.0
G_ps = 10.0
G_hp = 10.0

#Define thermal capacitance. Units: Joules/K.
C_p = 100.0

#Define our input noise damping time
dt_damp = 100.0

#Random changes for ambient per timestep
T_random = 0.1

#Measurement noise per timestep
T_noise = 0.001

#Our choice on what we're trying to optimize. We have no control over the ambient
#so forget that in the cost function. Mike think's that a cost function with a 
#1 in the [1,1] position is trying to minimise the RMS plate temperature. We probably
#actually want the RMS sensor temperature minimised - what Q matrix would that require?
#Lets only put a little weight on minimising heater current.
Q_mat = np.array([[0,0  ],
              [0,1.0]])
R_mat = np.array([[0.01**2]])

#Number of times
n_t = 10000

#For comparision, a simple proportional servo
servo_gain = 25 #Optimised by hand - applies to use_lqg=False
use_lqg=0
#------automatic below here------

#Define the matrices. Note that the vector has T_a then T_p
G_frac = G_hp*G_ah/(G_hp + G_ah) + G_ps*G_sa/(G_ps + G_sa)
A_mat = np.array([[-1/dt_damp,   0],    
                  [G_frac/C_p, -G_frac/C_p]])
#B is a column vector.
B_mat = np.array([[0], 
                  [G_hp/(G_hp + G_ah)/C_p]])
C_mat = np.array([[G_sa/(G_sa + G_ps), G_ps/(G_sa + G_ps)]])
V_mat = np.array([[T_random**2,0],
                  [0,0]])
W_mat = np.array([[T_noise**2]])

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
x = np.array([0.,0.])
x_history = np.empty( (n_t, 2) )
x_est = np.array([0.,0.])
x_est_history = np.empty( (n_t, 2) )
u = np.array([0])
u_history = np.empty( n_t )
for i in range(n_t):
    #Compute our estimator for x_{i+1}
    #First, what do we measure at this time?
    y = np.dot(C_mat, x) 
    y += np.random.multivariate_normal([0], W_mat)
    
    #Based on this measurement, what is the next value of x_est?
    x_est_new = np.dot(A_mat, x_est)
    x_est_new += np.dot(B_mat, u)
    dummy = y - np.dot(C_mat, (np.dot(A_mat, x) + np.dot(B_mat, u)))
    x_est_new += np.dot(K_mat, dummy)
    x_est = x_est_new
    x_est_history[i]=x_est
    
    # Now find u
    if use_lqg:
        u = -np.dot(L_mat, x_est)
    else:
        u = -servo_gain*y
    u_history[i] = u

    #Compute the actual x_i+1
    x += np.dot(A_mat, x)
    x += np.dot(B_mat, u)
    x += np.random.multivariate_normal([0,0], V_mat)
  
    #Save our history.
    x_history[i]=x
    
#Now what is our RMS?
print("RMS plate temperature: {0:6.4f}".format(np.std(x_history[:,1]))) 
