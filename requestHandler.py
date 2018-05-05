import motorDriver
import logData_Pi
import threading

_steps_from_zero = 0 #Number of steps from true south and home position
num_of_stp_per_deg_ra = 100 #Enter the number of steps per degree for the RA motor (43200 steps/h or 2880 steps/deg)
num_of_stp_per_deg_dec = 430 #Enter the number of steps per degree for the DEC motor (10000 steps/deg)

class requestHandle(object):
    def __init__(self, cfg_data):
        self.motor = motorDriver.motor()
        self.log_data = logData_Pi.logData(__name__)
        self.cfg_data = cfg_data
    
    def process(self, request):
        response = "None" #Variable to hold the response to be sent
        
        if (request == None) or (request == ""): #Check if the client is disconnected without any notice
            response = "None"
        elif request == "Test": #Respond to the connection testing command
            response = "OK"
        elif request == "Terminate": #Send the required response for the successful termination
            self.log_data.log("INFO", "Client requested connection termination.")
            response = "Bye"
        elif request == "Quit": #Send the 'Quit' response, which indicates server closing
            response == "Server closing"
        elif request == "Report Position" #Respond with the current position
            #Add code to calculate and send the current position of the telescope to the client as requested
            response = "POS_0_40_12_34" #RA_DEC_STPRA_STPDEC
        elif request == "TRKNGSTAT" #Send the tracking status of the telescope, whether is tracking or not
            response = "NO" #Value until full functionality is provided
        elif request == "SCALE": #Send the number of steps per degree for each motor
            response = "SCALEVALS_RA_%d_DEC_%d" %(num_of_stp_per_deg_ra, num_of_stp_per_deg_dec)
        else:
            self.log_data.log("INFO", "Received \'%s\' from client" %request)
            compon = request.split("_") #Get the components of the string
            if compon[0] == "TRNST":
                '''
                    #self.RAmotor
                    #Handle the transit function
                    #Get the RA and DEC and convert to number, after that calculate the number of steps
                    #Read from the log the current position to calculate the true steps needed to reach the required point
                    #Add a statement to check whether the motion is going to be to the left or to the right
                    #After that call the appropriate function from the motor driver file and set the delay to the maximum possible speed
                    #If RA is > 180 and < 0 or 360 then the motion will be to the right, otherwise to the left
                    #Or maybe if the number of required steps is < 0 then determine the motion
                '''
                
                ra_steps = float(compon[2])*num_of_stp_per_deg_ra #Number of RA steps from home position
                dec_steps = float(compon[4])*num_of_stp_per_deg_dec #Number of DEC steps from home position
                
                cur_stps = self.cfg_data.getSteps() #Get the current number of steps away from home position
                cur_stp_ra = cur_stps[0] #Get the current RA steps
                cur_stp_dec = cur_stps[1] #Get the current DEC steps
                home_calib = cur_stps[2] #Get the current home position calibration value
                
                #If the current steps variable is already corrected for a possible offset of home position from the true south, 
                #then remove the home_calib
                mov_stps_ra = float(cur_stp_ra) + ra_steps + float(home_calib) #Number of steps to move the RA motor
                mov_stps_dec = float(cur_stp_dec) + dec_steps + float(home_calib) #Number of steps to move the DEC motor
                
                #Get the current position of the dish from the magnetometer to use it later, before moving on
                
                #According to the sign of the mov_stps number decide at what direction to move, with negative indicating leftward direction
                #Replace the 1 in the arguments with the wanted delay and for the transit the speed is set to 200Hz or 0.005sec delay
                delay = 0.005 #Set the delay for the stepping
                if mov_stps_ra < 0:
                    ra_thr = threading.Thread(name = 'hourangle', target = self.motor.stepping_bckwd, args = (delay, -mov_stps_ra, True))
                else:
                    ra_thr = threading.Thread(name = 'hourangle', target = self.motor.stepping_fwd, args = (delay, mov_stps_ra, True))
                
                if mov_stps_dec < 0:
                    dec_thr = threading.Thread(name = 'declination', target = self.motor.stepping_bckwd, args = (delay, -mov_stps_dec, False))
                else:
                    dec_thr = threading.Thread(name = 'declination', target = self.motor.stepping_fwd, args = (delay, mov_stps_dec, False))
                ra_thr.start() #Start the thread for driving
                dec_thr.start() #Start the thread for driving
                while(not getattr(ra_thr, "done", False) or not getattr(dec_thr, "done", False)): #Wait until both threads finish
                    continue
                #ra_thr.join() #Close the thread
                #dec_thr.join() #Close the thread
                
                #An If statement is needed for the short code below, which is gonna check for successful dish placement
                response = "POSITION_SET" #Send the correct message as formated above
                self.log_data.log("INFO", "Dish position successfully set and client was informed.")
                #self.cfg_data.setSteps((mov_stps_ra, mov_stps_dec)) #If everything is successful then save the current telescope position
                
                #Use the magnetometer to determine the current position and if the dish moved correctly before sending any message
                #After checking the correctness of the position assign the correct message to the response variable
                #Also if the dish moved successfully, update the position in the settings file
                
                #ra_thr.run = False #Stops the execution of the thread
                #dec_thr.run = False #Stops the execution of the thread
                
                print("Received TRNST") #Used for debugging purposes
                
            elif compon[0] == "AAF":
                #Handle the aim and follow function
                print("Received AAF")
            elif compon[0] == "SCAN":
                #Handle the scan function
                print("Received SCAN")
            elif compon[0] == "SKYSCN":
                #Handle the sky scanning function
                print("Received SKYSCN")
            else:
                print("Invalid command")
                self.log_data.log("WARNING", "The command: %s, is not recognized as a valid server command, so no action taken." %request)
                response = "The command: %s, is not recognized as a valid server command." %request
        return response