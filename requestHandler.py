from PyQt5 import QtCore
from functools import partial
import motorDriver
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

    def start(self):
        self.serverThread.start()
        self.clientThread.start()
        self.server.requestProcess.connect(self.process)

        self.motor = motorDriver.MotorInit()
        self.motorMove = motorDriver.Stepping()
        # self.motorMove.motStepSig.connect(self.sendSteps)
        self.motorMove.motStepSig.connect(self.posObj.dataSend)
        self.motorMove.updtStepSig.connect(self.step_update)
        self.motorMove.motStopSig.connect(partial(self.server.sendDataClient.emit, "STOPPED_MOVING"))
        self.motorMove.motStartSig.connect(partial(self.server.sendDataClient.emit, "STARTED_MOVING"))

        self.motor.GPIO_Init()  # Initialize the GPIO pins on the Raspberry

        # Initialize the motor threads
        self.motorThread = QtCore.QThread()
        self.motorMove.moveToThread(self.motorThread)
        self.motorThread.start()

        self.positionThread.start()

    @QtCore.pyqtSlot(str, name='requestProcess')
    def process(self, request: str):
        print("Process handler called, handle msg: %s" % request)
        print("Process handler thread: %d" % int(QtCore.QThread.currentThreadId()))
        response = "Unrecognizable request"  # Variable to hold the response to be sent
        splt_req = request.split("_")

        if request == "CONNECT_CLIENT":
            self.client.reConnectSigC.emit()  # Attempt a client reconnection since the server should be running
            response = "Client notified to start"
        elif request == "START_SENDING_POS":
            self.positionThread.start()  # Start the position report thread
            response = "STARTED_SENDING_POS"
        elif request == "STOP_POS_SEND":
            self.positionThread.quit()
            response = "POSITION_REPORTING_HALTED"
        elif request == "SEND_POS_UPDATE":
            cur_pos = self.posObj.getPosition()  # Send an update of the current position
            self.client.sendData.emit("POSUPDATE_RA_%.5f_DEC_%.5f\n" % (float(cur_pos[0]), float(cur_pos[1])))
            response = "POS_UPDT_SENT"
        elif request == "STOP":  # TODO implement the stop request in a better way
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
            response = "OK"  # Just send a response to confirm communication
        elif request == "Terminate":  # Send the required response for the successful termination
            # TODO should we only do logging?
            self.log_data.info("Client requested connection termination.")
            self.server.releaseClient()
            response = "Bye"
        elif request == "Quit":  # Send the 'Quit' response, which indicates server closing
            # TODO implement a server closure
            response = "Server closing"
        elif request == "TRKNGSTAT":  # Send the tracking status of the telescope, whether is tracking or not
            # TODO make a function to get the current tracking status based on the moving of the motors
            response = "NO"  # Value until full functionality is provided
        elif request == "SCALE":  # Send the number of steps per degree for each motor
            # TODO send the steps per degree for the motors, may be removed in later release
            response = "SCALEVALS_RA_%d_DEC_%d" % (num_of_stp_per_deg_ra, num_of_stp_per_deg_dec)
        elif request == "SEND_HOME_STEPS":
            home_stps = self.cfg_data.getSteps()  # Get the saved steps
            response = "STEPS-FROM-HOME_%.0f_%.0f" % (home_stps[0], home_stps[1])  # Right ascension first value
        elif request == "RETURN_HOME":  # Return to home position
            freq = 200.0  # Set the maximum frequency
            home_stps = self.cfg_data.getSteps()  # Get the saved steps
            self.motorMove.moveMotSig.emit("%.1f_%.1f_%d_%d" % (freq, freq, -int(home_stps[0]), -int(home_stps[1])))
        elif splt_req[0] == "TRNST":
            ra_steps = float(splt_req[2]) * motorDriver.ra_steps_per_deg
            dec_steps = float(splt_req[4]) * motorDriver.dec_steps_per_deg
            freq = 200.0  # Set the maximum frequency
            self.motorMove.moveMotSig.emit("%.1f_%.1f_%d_%d" % (freq, freq, int(ra_steps), int(dec_steps)))

        self.server.sendDataClient.emit(response)  # Send the response to the client

    ''''@QtCore.pyqtSlot(str, int, name='motorStepCount')
    def sendSteps(self, typ: str, stp: int):
        string = typ + "_" + str(stp) + "\n"
        self.server.sendDataClient.emit(string)'''

    @QtCore.pyqtSlot(list, name='updateSteps')
    def step_update(self, data: list):
        self.cfg_data.setSteps(data)
