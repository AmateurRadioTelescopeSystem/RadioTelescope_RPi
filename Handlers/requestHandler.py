from PyQt5 import QtCore
from functools import partial
from Handlers import motorDriver
import logging
import sys

_steps_from_zero = 0  # Number of steps from true south and home position
num_of_stp_per_deg_ra = 2880  # Enter the number of steps per degree for the RA motor (43200 steps/h or 2880 steps/deg)
num_of_stp_per_deg_dec = 10000  # Enter the number of steps per degree for the DEC motor (10000 steps/deg)


class requestHandle(QtCore.QObject):
    def __init__(self, cfg_data, server, client, posObj, servThread, clientThread, positionThread, parent=None):
        super(requestHandle, self).__init__(parent)  # Get the parent of the class
        self.log_data = logging.getLogger(__name__)  # Get the logging object
        self.cfg_data = cfg_data
        self.server = server
        self.client = client
        self.positionThread = positionThread
        self.serverThread = servThread
        self.clientThread = clientThread
        self.posObj = posObj  # Dish position object
        self.tracking_command = False  # Indicator if we need tracking or not

        # Keep the tracking speeds sent by the user
        self.trk_speed_ra = 0
        self.trk_speed_dec = 0

    def start(self):
        self.serverThread.start()
        self.clientThread.start()
        self.server.requestProcess.connect(self.process)

        cur_stps = self.cfg_data.getSteps()  # Get the current steps from home to add them initially

        self.motor = motorDriver.MotorInit()
        self.motorMove = motorDriver.Stepping(cur_stps[0], cur_stps[1])
        self.motorMove.motStepSig.connect(self.posObj.dataSend)
        self.motorMove.updtStepSig.connect(self.step_update)
        self.motorMove.motStopSig.connect(partial(self.server.sendDataClient.emit, "STOPPED_MOVING"))
        self.motorMove.motStopSig.connect(self.tracker)  # Send the tracking command if the user requested it
        self.motorMove.motStartSig.connect(partial(self.server.sendDataClient.emit, "STARTED_MOVING"))

        self.server.clientDisconnected.connect(partial(self.motor.enabler, False))  # Disable motors

        self.motor.GPIO_Init()  # Initialize the GPIO pins on the Raspberry

        # Initialize the motor threads
        self.motorThread = QtCore.QThread()
        self.motorMove.moveToThread(self.motorThread)
        self.motorThread.start()

        self.positionThread.start()

    @QtCore.pyqtSlot(str, name='requestProcess')
    def process(self, request: str):
        self.log_data.debug("Process handler called, handle msg: %s" % request)  # Used for debugging purposes
        response = "Unrecognizable request\n"  # Variable to hold the response to be sent
        splt_req = request.split("_")  # Split the received string using the specified delimiter

        if request == "CONNECT_CLIENT":
            self.client.reConnectSigC.emit()  # Attempt a client reconnection since the server should be running
            response = "Client notified to start\n"

        elif request == "START_SENDING_POS\n":
            self.positionThread.start()  # Start the position report thread
            response = "STARTED_SENDING_POS\n"
        elif request == "STOP_POS_SEND":
            self.positionThread.quit()
            response = "POSITION_REPORTING_HALTED\n"
        elif request == "SEND_POS_UPDATE":
            cur_pos = self.posObj.getPosition()  # Send an update of the current position
            self.client.sendData.emit("POSUPDATE_RA_%.5f_DEC_%.5f\n" % (float(cur_pos[0]), float(cur_pos[1])))
            response = "POS_UPDT_SENT\n"

        elif request == "STOP":  # TODO implement the stop request in a better way
            self.motor.clean_IO()  # Clean-up GPIO before exit
            sys.exit()  # Exit from the application as per request
        elif splt_req[0] == "MANCONT":  # TODO implement the manual control in a better way
            if len(splt_req) == 5:
                freq = splt_req[2]
                step_ra = splt_req[3]
                step_dec = splt_req[4]
                if splt_req[1] == "MOVRA":
                    # TODO make the string more intuitive by including field names
                    self.motorMove.moveMotSig.emit("%s_%s_%s_%d" %(freq, freq, step_ra, 0))
                elif splt_req[1] == "MOVDEC":
                    self.motorMove.moveMotSig.emit("%s_%s_%d_%s" % (freq, freq, 0, step_dec))
                elif splt_req[1] == "MOVE":
                    self.motorMove.moveMotSig.emit("%s_%s_%s_%s" % (freq, freq, step_ra, step_dec))
            elif splt_req[1] == "STOP":
                self.motorMove.moveMotSig.emit("-1_-1_0_0")  # Send a negative frequency to indicate stopping

        elif request == "Test":  # Respond to the connection testing command
            response = "OK\n"  # Just send a response to confirm communication
        elif request == "Terminate":  # Send the required response for the successful termination
            # TODO should we only do logging?
            self.log_data.info("Client requested connection termination.")
            self.server.releaseClient()
            response = "Bye\n"
        elif request == "Quit":  # Send the 'Quit' response, which indicates server closing
            # TODO implement a server closure
            response = "Server closing\n"

        # Motor control section
        elif request == "ENABLE_MOTORS":
            self.motor.enabler(True)
            response = "MOTORS_ENABLED\n"
        elif request == "DISABLE_MOTORS":
            self.motor.enabler(False)
            response = "MOTORS_DISABLED\n"
        elif request == "REPORT_MOTOR_STATUS":
            if self.motor.motor_status():
                response = "MOTORS_ENABLED\n"  # Return the status of motors (Enabled/Disabled)
            else:
                response = "MOTORS_DISABLED\n"

        elif request == "TRKNGSTAT":  # Send the tracking status of the telescope, whether is tracking or not
            # TODO make a function to get the current tracking status based on the moving of the motors
            response = "NO\n"  # Value until full functionality is provided
        elif request == "SCALE":  # Send the number of steps per degree for each motor
            # TODO send the steps per degree for the motors, may be removed in later release
            response = "SCALEVALS_RA_%d_DEC_%d\n" % (num_of_stp_per_deg_ra, num_of_stp_per_deg_dec)
        elif request == "SEND_HOME_STEPS":
            home_stps = self.cfg_data.getSteps()  # Get the saved steps
            response = "STEPS-FROM-HOME_%.0f_%.0f\n" % (home_stps[0], home_stps[1])  # Right ascension first value
        elif request == "RETURN_HOME":  # Return to home position
            freq = 200.0  # Set the maximum frequency
            home_stps = self.cfg_data.getSteps()  # Get the saved steps
            self.motorMove.moveMotSig.emit("%.1f_%.1f_%d_%d" % (freq, freq, -int(home_stps[0]), -int(home_stps[1])))

        elif splt_req[0] == "TRNST":
            freq = 200.0  # Set the maximum frequency
            cur_stps = self.cfg_data.getSteps()  # Read the current steps from home to compensate for it
            ra_steps = float(splt_req[2]) * motorDriver.ra_steps_per_deg - float(cur_stps[0])
            dec_steps = float(splt_req[4]) * motorDriver.dec_steps_per_deg - float(cur_stps[1])
            self.motorMove.moveMotSig.emit("%.1f_%.1f_%d_%d" % (freq, freq, int(ra_steps), int(dec_steps)))
        elif splt_req[0] == "TRK":
            freq = 200.0  # Set the maximum frequency

            cur_stps = self.cfg_data.getSteps()  # Read the current steps from home to compensate for it
            ra_steps = float(splt_req[2]) * motorDriver.ra_steps_per_deg - float(cur_stps[0])
            dec_steps = float(splt_req[4]) * motorDriver.dec_steps_per_deg - float(cur_stps[1])

            self.trk_speed_ra = float(splt_req[6])
            self.trk_speed_dec = float(splt_req[8])
            self.motorMove.moveMotSig.emit("%.1f_%.1f_%d_%d" % (freq, freq, int(ra_steps), int(dec_steps)))
            self.tracking_command = True  # Enable the tracking command, so on motor stop the tracking is triggered

        self.server.sendDataClient.emit(response)  # Send the response to the client

    @QtCore.pyqtSlot(name='motionStopNotifierSignal')
    def tracker(self):
        if self.tracking_command:
            # Individual motor stepping frequencies
            if (self.trk_speed_ra == 0.0) and (self.trk_speed_dec == 0.0):
                freq1 = freq2 = 12  # Set a stellar tracking speed
                ra_steps = 345600  # Enough steps to track for 8 hours
                dec_steps = 0  # Declination is not changing is stellar objects, so we do not move this motor
            else:
                freq1 = 12 + self.trk_speed_ra*num_of_stp_per_deg_ra
                freq2 = self.trk_speed_dec*num_of_stp_per_deg_dec

                ra_steps = 345600  # Enough steps to track for 8 hours
                dec_steps = 345600  # Enough steps for 8 hours of tracking

            self.tracking_command = False  # Reset tracking command
            self.motorMove.moveMotSig.emit("%.1f_%.1f_%d_%d" % (freq1, freq2, int(ra_steps), int(dec_steps)))

    @QtCore.pyqtSlot(list, name='updateSteps')
    def step_update(self, data: list):
        self.cfg_data.setSteps(data)
