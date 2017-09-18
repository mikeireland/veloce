# Simulator output function for least squares optimisation
import csv
import numpy as np
voltage = 23.68 #voltage to heaters
heater_resistance  = 10 #individual heater resistance ohms
##input data conditioning
def read_data(logfile):
    #read in log file
    rr = csv.reader(open(logfile,'r'))
    temp_time = [] #Unix timestamps
    ts7 = [] #Optical table
    ts4 = [] #Bottom
    ts2 = [] #Upper
    ta = [] #Ambient Temperatures
    #heater channel values
    heat_time = []
    hch1 = []
    hch2 = []
    hch3 = []
    hch4 = []
    for row in rr:
        if row[3].lstrip() == 'TEMPS':
            #read in temps from file
            temp_time.append(float(row[1]))
            ts7.append(float(row[4]))
            ts4.append(float(row[5]))
            ts2.append(float(row[6]))
            ta.append(float(row[7]))
        if row[3].lstrip() == 'HEATERS':
            #read in heater fractions from the file in multiply by their respective power values
            heat_time.append(float(row[1]))
            hch1.append(float(row[4]))
            hch2.append(float(row[5]))
            hch3.append(float(row[6]))
            hch4.append(float(row[7]))
    #convert to numpy arrays
    temp_time = np.array(temp_time)
    ts7 = np.array(ts7)
    ts4 = np.array(ts4)
    ts2 = np.array(ts2)
    ta = np.array(ta)
    heat_time = np.array(heat_time)
    hch1 = np.array(hch1)
    hch2 = np.array(hch2)
    hch3 = np.array(hch3)
    hch4 = np.array(hch4)
    # convert heater to powers and correct format
    #hch1 ----> Long sides h1,h3 
    #hch2 ----> Short side h5,h6
    #hch3 ----> Top side h2
    #hch4 ----> Bottom side h4
    h3 = h1 = (hch1*voltage**2)/(heater_resistance*6) #sides 1 and 2 have 6 heaters in series
    h5 = h6 = (hch2*voltage**2)/(heater_resistance*6) #sides 5 and 6 have 6 heater in series
    h2 = (3*hch3*voltage**2)/(heater_resistance*6) #top has the series strings of 6 in paralell CHECK!!!
    h4 = (3*hch3*voltage**2)/(heater_resistance*6) #bottom has the series strings of 6 in paralell CHECK!!!
    
    raw_temp = np.zeros( (4,len(ts2)) )
    #import pdb; pdb.set_trace()
    raw_temp[0,:] = ts2
    raw_temp[1,:] = ts4
    raw_temp[2,:] = ts7
    raw_temp[3,:] = ta
    temp_time = temp_time - temp_time[0]
    raw_heater = np.zeros( (6,len(h1)) )
    raw_heater[0,:] = h1
    raw_heater[1,:] = h2
    raw_heater[2,:] = h3
    raw_heater[3,:] = h4
    raw_heater[4,:] = h5
    raw_heater[5,:] = h6
    heat_time = heat_time - heat_time[0]
    return raw_temp, temp_time, raw_heater, heat_time

    
def condition_data(sampling_timestep, logfile):
    dt = sampling_timestep
    #read in log file
    rr = csv.reader(open(logfile,'r'))
    temp_time = [] #Unix timestamps
    ts7 = [] #Optical table
    ts4 = [] #Bottom
    ts2 = [] #Upper
    ta = [] #Ambient Temperatures
    #heater channel values
    heat_time = []
    hch1 = []
    hch2 = []
    hch3 = []
    hch4 = []
    for row in rr:
        if row[3].lstrip() == 'TEMPS':
            #read in temps from file
            temp_time.append(float(row[1]))
            ts7.append(float(row[4]))
            ts4.append(float(row[5]))
            ts2.append(float(row[6]))
            ta.append(float(row[7]))
        if row[3].lstrip() == 'HEATERS':
            #read in heater fractions from the file in multiply by their respective power values
            heat_time.append(float(row[1]))
            hch1.append(float(row[4]))
            hch2.append(float(row[5]))
            hch3.append(float(row[6]))
            hch4.append(float(row[7]))
    #convert to numpy arrays
    temp_time = np.array(temp_time)
    ts7 = np.array(ts7)
    ts4 = np.array(ts4)
    ts2 = np.array(ts2)
    ta = np.array(ta)
    heat_time = np.array(heat_time)
    hch1 = np.array(hch1)
    hch2 = np.array(hch2)
    hch3 = np.array(hch3)
    hch4 = np.array(hch4)
    # convert heater to powers and correct format
    #hch1 ----> Long sides h1,h3 
    #hch2 ----> Short side h5,h6
    #hch3 ----> Top side h2
    #hch4 ----> Bottom side h4
    h3 = h1 = (hch1*voltage**2)/(heater_resistance*6) #sides 1 and 2 have 6 heaters in series
    h5 = h6 = (hch2*voltage**2)/(heater_resistance*6) #sides 5 and 6 have 6 heater in series
    h2 = (3*hch3*voltage**2)/(heater_resistance*6) #top has the series strings of 6 in paralell CHECK!!!
    h4 = (3*hch3*voltage**2)/(heater_resistance*6) #bottom has the series strings of 6 in paralell CHECK!!!
    
    #now we must sample this data at a the rate specified by the timestep and average over the values
    #first do temperatures
    integral_temp = np.zeros( (4, 1) )
    integral_heater = np.zeros( (6, 1) )
    samplestep = 1
    time = 0
    sample_temp = np.zeros( (4,1) )
    sample_heater = np.zeros( (6,1) )
    for step in range(1, len(temp_time)):
        #integrate temperatures
        integral_temp[0,0] += 0.5*(ts2[step -1] + ts2[step])*(temp_time[step] - temp_time[step - 1])
        integral_temp[1,0] += 0.5*(ts4[step -1] + ts4[step])*(temp_time[step] - temp_time[step - 1])
        integral_temp[2,0] += 0.5*(ts7[step -1] + ts7[step])*(temp_time[step] - temp_time[step - 1])
        integral_temp[3,0] += 0.5*(ta[step -1] + ta[step])*(temp_time[step] - temp_time[step - 1])
        #integrate heaters
        integral_heater[0,0] += 0.5*(h1[step -1] + h1[step])*(heat_time[step] - heat_time[step - 1])
        integral_heater[1,0] += 0.5*(h2[step -1] + h2[step])*(heat_time[step] - heat_time[step - 1])
        integral_heater[2,0] += 0.5*(h3[step -1] + h3[step])*(heat_time[step] - heat_time[step - 1])
        integral_heater[3,0] += 0.5*(h4[step -1] + h4[step])*(heat_time[step] - heat_time[step - 1])
        integral_heater[4,0] += 0.5*(h5[step -1] + h5[step])*(heat_time[step] - heat_time[step - 1])
        integral_heater[5,0] += 0.5*(h6[step -1] + h6[step])*(heat_time[step] - heat_time[step - 1])
        #import pdb; pdb.set_trace()
        time += temp_time[step] - temp_time[step - 1]
        
        if (temp_time[step] - temp_time[0]) > samplestep*dt: #each timestep take average
            sample_temp = np.append(sample_temp, integral_temp/time, axis=1)
            #np.append(sample_heater, integral_heater/dt)
            integral_temp = np.zeros( (4, 1) )
            #integral_heater = np.zeros( (6, 1) )
            samplestep += 1
    #cut zeros off begining of output arrays
    #sample_temp = sample_temp[:,1:len(sample_temp[0,:])]
    #sample_heater = sample_heater[:,1:len(sample_heater[0,:])]
    return sample_temp, sample_heater
            
        
def simulate(constants, temps, temp_times, heaters, heater_times, return_temps=False):
    
    """
    Parameters
    ----------
    constants: numpy array
    
    times_in:
    
    temps_in: [3,n_times] array
    
    return_temps: bool (optional)
        If true, return the modelled temperatures at each timestes [3,n_times]
        Otherwise, return a flattened version of temps_model = temps_in
    
    Returns
    -------
    temps or residuals
    """

    individual_ghp = constants[0]
    gpb_total = constants[1]
    gpb7 = constants[2]
    gpa_total = constants[3]
    gps = constants[4]
    gsb = constants[5]
    individual_gih = constants[6]
    linear_cond = constants[7]
    table_cond = constants[8]
    individual_ch = constants[9]
    lid_total = constants[10]
    cp7 = constants[11]
    cb = constants[12]
    cp4 = constants[13]
    linear_cond_bottom = constants[14]
    #DEFINE SIMULATION LOOP MATRIX CONSTANTS
    #a lot of sides can be determined relative to each other by surface area ratios
    # long sides(1.94 x 0.66), short sides (1.54 x 0.66), top/bottom (1.54 x 1.94)
    total_sa = 2*(1.94*0.66 + 1.54*0.66 + 1.94*1.54)
    #----individual fractions of total system qauntity that each side type should have based on surface area ratio
    #----side number designations----see doco - curently M.R. thesis
    #SIDE       NUMBER      COUPLING
    #LONG A     1           2,4,5,6,7
    #TOP        2           1,3,5,6
    #LONG B     3           2,4,5,6,7
    #BOTTOM     4           1,3,5,6,7
    #SHORT A    5           1,2,3,4,7
    #SHORT B    6           1,2,3,4,7
    #OPTICAL    7           1,3,4,5,6       
    long_frac = 1.94*0.66/total_sa #sides 1,3
    short_frac = 1.54*0.66/total_sa #sides 5,6
    topbottom_frac = 1.94*1.54/total_sa #sides 2,4

    #Gah - conductance between heater and the ambient - model as 0 for simplictiy, add if needed later
    gah1 = gah2 = gah3 = gah4 = gah5 = gah6 = 0 

    #ghp - conductance between heaters and plates, defined by the conductance for an individual heater and # of heaters on each of the sides W/K
    #individual_ghp = 192.6
    ghp1 = ghp3 = ghp5 = ghp6 = 6*individual_ghp
    ghp2 = ghp4 = 18*individual_ghp

    #Gpb - conductance between plate and internal air temperature t_b
    #defined by estimated total system values W/K
    #gpb_total = 264.0594
    gpb1 = gpb3 = long_frac*gpb_total
    gpb5 = gpb6 = short_frac*gpb_total
    gpb2 = gpb4 = topbottom_frac*gpb_total

    #gpb7 = 74.2374
    #gpa - conduction between plates and ambient W/K
    #gpa_total = 7.6962
    gpa1 = gpa3 = long_frac*gpa_total
    gpa5 = gpa6 = short_frac*gpa_total
    gpa2 = gpa4 = topbottom_frac*gpa_total
    #Gps - conduction between plate and sensor W/K
    #gps = 0.4599
    gps2 = gps4 = gps7 = gps
    #Gsb - conduction between sensor and enclosure air temperature W/K
    #gsb = 0.003
    gsb2 = gsb4 = gsb7 = gsb
    #Gih - conduction betweeen internal heater temperature and exterior of heater casing W/K
    #individual_gih = 85.719
    gih1 = gih3 = gih5 = gih6 = 6*individual_gih
    gih2 = gih4 = 18*individual_gih
    #gnm - conduction between sides and optical table, proportional to the length of intersection between the sides for the sides while optical table is different
    #this assumes thickness of joins are the same for all sides
    #linear_cond = 1,366.6667 #W/K/mm
    #--three different types
    #but bottom is different since it is bolted on
    #BOTTOM
    g14 = g34 = 1940*linear_cond_bottom*10**(-3)
    g45 = g46 = 1540*linear_cond_bottom*10**(-3)
    #1940mm
    g23 = g12 = 1940*linear_cond*10**(-3)
    #1540mm
    g25 = g26 = 1540*linear_cond*10**(-3)
    #660mm
    g15 = g35 = g36 = g16 = 660*linear_cond*10**(-3)
    #optical table will couple differently
    #table_cond =1.125
    g17 = g27 = g37 = g47 = g57 = g67 = table_cond

    #ch - heater thermal capacitances J/K
    #individual_ch = 29.8552579523659
    ch1 = ch3 = ch5 = ch6 = individual_ch*6 #heater thermal capacitance of the short and long sides
    ch2 = ch4 = individual_ch*18 #heater thermal capacitance of top and bottom, 3x greater due to 3x more heaters
    
    #cp - plate thermal capacitances J/K
    #cp_total = 40000
    #in testing bottom plate was found to exhibit different behaviour to the top plate, so define different area ratios
    lid_sa = 1.94*1.54 + 2*(1.94*0.66 + 1.54*0.66) # surface area of lid of enclosure
    cp2 = (1.94*1.54/lid_sa)*lid_total
    cp1 = cp3 = (1.94*0.66/lid_sa)*lid_total
    cp5 = cp6 = (1.54*0.66/lid_sa)*lid_total
    #cp7 = 100000 #optical table approx 200kg of Al
    #cb - Internal air thermal capacitance J/K
    #cb = 2387.88 #J/K
    #dt_damp ambient noise dampening constant
    #dt_damp = 1000
    
    A_sim= np.array([ [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,], 
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

    #Simulation variables
    t_end = 0
    #import pdb; pdb.set_trace()
    if temp_times[temp_times.size - 1] > heater_times[heater_times.size - 1]:
        t_end = temp_times[temp_times.size - 1]
    else:
        t_end = heater_times[heater_times.size - 1]
    dt = 0.05 #the integration timestep
    timesteps = int(round(t_end/dt)) #number of integration timesteps
    xvalues = np.zeros( (15, timesteps) ) #array of x vectors
    yvalues = np.zeros( (3, timesteps) ) # setup a vector to write simulated yvalues to
    ycomp = np.zeros( (3, timesteps) )
    
    ycomp[:,0:1] = temps[0:3,0:1]
    xvalues[:,0:1] = constants[15:31] #set initial state vector based on initial sensor readings 
    yvalues[:,0:1] = temps[0:3,0:1] #set initial output based on initial state vector 
    
    temps_index = 0
    heaters_index = 0
    #now simulate!
    for step in range(1, timesteps):
        #update temperature index
        if step*dt > temp_times[temps_index + 1]:
            temps_index += 1
        if step*dt > heater_times[heaters_index + 1]:
            heaters_index += 1
        #simulate this timestep
        xdot = np.dot(A_sim, xvalues[:, (step -1):step]) + np.dot(B_sim, heaters[:, heaters_index:(heaters_index + 1)])
        xvalues[:,step:(step + 1)] = xvalues[:, (step - 1):step] + xdot*dt
        yvalues[:,step:(step + 1)] = np.dot(C_sim, xvalues[:, (step -1):step])
        #set ambient
        xvalues[0,step] = temps[3,temps_index]
        #record sensor values to compare
        ycomp[:,step:(step + 1)] = temps[0:3, temps_index:(temps_index + 1)]
    if return_temps:
        return yvalues
    else:
        #compute residuals and flatten
        return (yvalues - ycomp).flatten()

def run_optimisation():
    #set initialvalues to pass to simulator
    file = "C:\\Users\\mattr\\OneDrive\\Documents\\Stromolo Job\\Testheater0.log"
    constants = 25*np.ones( (30,1) )
    constants[0] = 192.6 #individual_ghp
    constants[1] = 264.0594 #gpb_total
    constants[2] = 74.2374 #gpb7
    constants[3] = 7.6962 #gpa_total
    constants[4] = 0.4599 #gps
    constants[5] = 0.003 #gsb
    constants[6] = 85.719  #individual_gih
    constants[7] = 1366.6667 #linear conductance lid
    constants[8] = 1.125 #optical table conductance to other sides
    constants[9] = 29.8553 #individual_ch
    constants[10] = 82898.64 #lid cp
    constants[11] = 234879.48 #table cp
    constants[12] = 2387.88 #cb
    constants[13] = 46054.8 #bottom cp
    constants[14] = 1366.6667 #bottom linear conductance
    raw_temp, temp_time, raw_heater, heat_time = read_data(file)
    output = simulate(constants, raw_temp, temp_time, raw_heater, heat_time, True)
    import pdb; pdb.set_trace()
    