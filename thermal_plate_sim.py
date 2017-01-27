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
dt_damp = 1000.0

#Random changes for ambient per timestep
T_random = 0.1

#Measurement noise per timestep
T_noise = 0.001

#Our choice on what we're trying to optimize. We have no control over the ambient
#so forget that in the cost function. Lets only put a little weight on minimising heater
#current.
Q_mat = np.array([[0,0  ],
              [0,1.0]])
R_mat = np.array([[0.01**2]])

#Number of times
n_t = 10000
#------automatic below here------

#Define the matrices. Note that the vector has T_a then T_p
G_frac = G_hp*G_ah/(G_hp + G_ah) + G_ps*G_sa/(G_ps + G_sa)
A_mat = np.array([[-1/dt_damp,   0],    
                  [G_frac/C_p, -G_frac/C_p]])
B_mat = np.array([[0, G_hp/(G_hp + G_ah)/C_p]])
C_mat = np.array([[G_sa/(G_sa + G_ps), G_ps/(G_sa + G_ps)]])
V_mat = np.array([[T_random**2,0],
                  [0,0]])
W_mat = np.array([[T_noise**2]])

#P_mat = la.solve_discrete_are(A_mat, C_mat, V_mat, W_mat)
#S_mat = la.solve_discrete_are(A_mat, B_mat, Q_mat, R_mat)

#Simulate without feedback for now...
x = np.array([0.,0.])
x_history = np.empty( (n_t, 2) )
for i in range(n_t):
    x += np.dot(A_mat, x)
    x += np.random.multivariate_normal([0,0], V_mat)
    # Now find u
    
    #Save our history.
    x_history[i]=x