"""Put all the LQG mathematics here so that it can be tested separately to the servo
loop"""

from __future__ import division, print_function
import numpy as np
import scipy.linalg as la

lqg_dt = 0.3

#Define thermal conductivities. Units: Watts/K.
#with 3.409W (HEATER_MAX) on, we have an equilibrium
#temperature about 11 degrees above ambient. This
#equates to a coupling of 0.15 Watts/K for each side
#of the plate. 
G_sa = 0.15 #Vacuum radiative coupling would be 0.1, with black surfaces.
G_ah = 0.15
G_ps = 1000.0
G_hp = 1000.0
G_ih = 18
#Define thermal capacitance. Units: Joules/K.
C_p = 393.0 #Should be 393. Oritinally 860.0
C_h = 60
#Define our input noise damping time
dt_damp = 1000.0

#Random changes for ambient per second, in K.
#FIXME: this should probably automatically change when the timestep changes
T_random = 0.01*lqg_dt

#Measurement noise per second
T_noise = 0.001*lqg_dt

#so forget that in the cost function. Mike think's that a cost function with a 
#1 in the [1,1] position is trying to minimise the RMS plate temperature. We 
#actually want the RMS sensor temperature minimised - what Q matrix would that 
#Lets only put a little weight on minimising heater current.
#FIXME: Delete this when the Q_mat below is tested.
#Q_mat = np.array([[0,0  ],
#    [0,1.0]])
    
#Better Q matrix, which needs checking
#3x3 Q

Q_mat = np.array([[(G_sa**2)/((G_ps+G_sa)**2), 0, G_sa*G_ps/((G_ps+G_sa)**2)], [0, 0, 0],
                    [G_sa*G_ps/((G_ps+G_sa)**2), 0, (G_ps**2)/((G_ps+G_sa)**2)]])

#2x2 Q
'''
Q_mat = np.array([[(G_sa**2)/((G_ps+G_sa)**2), G_sa*G_ps/((G_ps+G_sa)**2)],
                    [G_sa*G_ps/((G_ps+G_sa)**2), (G_ps**2)/((G_ps+G_sa)**2)]])
#Q_mat gain
'''
Q_mat = Q_mat*1
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

#The "R" matrix, which balances wanting small heater outputs with maintaining
#temperature.
#FIXME: This seems to bias the algorithm if heater outputs can only be 
#positive.
R_mat = np.array([[0.001**2]])


#Define the matrices. Note that the vector has T_a then T_i then T_p
G_frac = G_hp*G_ah/(G_hp + G_ah) + G_ps*G_sa/(G_ps + G_sa)
A_mat = np.array([[-1/dt_damp,   0, 0],    
           [G_ah*G_ih/(C_h*(G_ah+G_hp+G_ih)), (1/C_h)*((G_ih**2)/(G_ah+G_hp+G_ih)-G_ih), G_hp*G_ih/(C_h*(G_ah+G_hp+G_ih))],
       [(1/C_p)*(G_ah*G_hp/(G_ah+G_hp+G_ih)+G_ps*G_sa/(G_ps+G_sa)), G_hp*G_ih/(C_p*(G_ah+G_hp+G_ih)), (1/C_p)*(-G_hp+(G_hp**2)/(G_ah+G_hp+G_ih)-G_ps+(G_ps**2)/(G_ps+G_sa))]])
#Scale A_mat by the timestep and add the identity matrix because we are
#operating discrete time
#B is a column vector.
B_mat = np.array([[0], 
    [1/C_h],
    [0]])

C_mat = np.array([[G_sa/(G_sa + G_ps), 0, G_ps/(G_sa + G_ps)]])



#FIXME: Not 100% certain that this is correct.
A_mat = np.eye(len(A_mat)) + lqg_dt*A_mat
           

#Scale by the timestep
B_mat *= lqg_dt

 #3x3 V
V_mat = np.array([[T_random**2,0,0],
                          [0,0,0], [0, 0, 0]])
'''
#2x2 V
V_mat = np.array([[T_random**2,0],
                          [0, 0]])
'''

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

