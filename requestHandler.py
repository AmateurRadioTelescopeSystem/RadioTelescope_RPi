from PyQt5 import QtCore
import logData_Pi
import motorDriver
import sys

_steps_from_zero = 0  # Number of steps from true south and home position
num_of_stp_per_deg_ra = 100  # Enter the number of steps per degree for the RA motor (43200 steps/h or 2880 steps/deg)
num_of_stp_per_deg_dec = 430  # Enter the number of steps per degree for the DEC motor (10000 steps/deg)


class requestHandle(QtCore.QObject):
    def __init__(self, cfg_data, server, client, posObj, servThread, clientThread, positionThread, parent=None):
        super(requestHandle, self).__init__(parent)  # Get the parent of the class
        self.log_data = logData_Pi.logData(__name__)
        self.cfg_data = cfg_data
        self.server = server
        self.client = client
        self.positionThread = positionThread
        self.serverThread = servThread
        self.clientThread = clientThread
        self.posObj = posObj

    def start(self):
        print("Handler thread started ID: %d" % int(QtCore.QThread.currentThreadId()))
        self.serverThread.start()
        self.clientThread.start()
        self.server.requestProcess.connect(self.process)

        self.motor = motorDriver.MotorInit()
        self.motorMove = motorDriver.Stepping()

        self.motor.GPIO_Init()  # Initialize the GPIO pins on the Raspberry

        # Initialize the motor threads
        self.motorThread = QtCore.QThread()
        self.motorMove.moveToThread(self.motorThread)
        self.motorThread.start()

    @QtCore.pyqtSlot(str, name='requestProcess')
    def process(self, request: str):
        print("Process handler called, handle msg: %s" % request)
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
            cur_pos = self.posObj.getPosition()
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
                    self.motorMove.moveMotSig.emit("%s_%s_%s_%d" %(freq, freq, step_ra, 0))
                elif splt_req[1] == "MOVDEC":
                    self.motorMove.moveMotSig.emit("%s_%s_%d_%s" % (freq, freq, 0, step_dec))
                elif splt_req[1] == "MOVE":
                    self.motorMove.moveMotSig.emit("%s_%s_%s_%s" % (freq, freq, step_ra, step_dec))
            elif splt_req[1] == "STOP":
                self.motorMove.moveMotSig.emit("-1_-1_0_0")  # Send a negative frequency to indicate stopping
            response = "Command executed for man cont"

        elif request == "Test":  # Respond to the connection testing command
            response = "OK"
        elif request == "Terminate":  # Send the required response for the successful termination
            self.log_data.log("INFO", "Client requested connection termination.")
            self.server.releaseClient()
            response = "Bye"
        elif request == "Quit":  # Send the 'Quit' response, which indicates server closing
            response = "Server closing"
        elif request == "Report Position":  # Respond with the current position
            # Add code to calculate and send the current position of the telescope to the client as requested
            response = "POS_0_40_12_34"  # RA_DEC_STPRA_STPDEC
        elif request == "TRKNGSTAT":  # Send the tracking status of the telescope, whether is tracking or not
            response = "NO"  # Value until full functionality is provided
        elif request == "SCALE":  # Send the number of steps per degree for each motor
            response = "SCALEVALS_RA_%d_DEC_%d" % (num_of_stp_per_deg_ra, num_of_stp_per_deg_dec)

        self.server.sendDataClient.emit(response)  # Send the response to the client

