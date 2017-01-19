import veloce

#Initialise our thermal_verver object
tc = veloce.thermal_control.ThermalControl()
server_cmds = veloce.thermal_control_cmds.CommandList(tc)
#The following line starts the server.
thermal_server = veloce.server.ServerSocket(3000, "VTherm", server_cmds)

#Add jobs we want to test.
thermal_server.add_job(tc.job_doservo)

#Run!
thermal_server.run()
