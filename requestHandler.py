from PyQt5 import QtCore
import motorDriver
import logData_Pi

_steps_from_zero = 0  # Number of steps from true south and home position
num_of_stp_per_deg_ra = 100  # Enter the number of steps per degree for the RA motor (43200 steps/h or 2880 steps/deg)
num_of_stp_per_deg_dec = 430  # Enter the number of steps per degree for the DEC motor (10000 steps/deg)


class requestHandle(QtCore.QObject):
    def __init__(self, cfg_data, server, client, parent=None):
        super(requestHandle, self).__init__(parent)  # Get the parent of the class
        self.motor = motorDriver.motor()
        self.log_data = logData_Pi.logData(__name__)
        self.cfg_data = cfg_data
        self.server = server
        self.client = client

    def start(self):
        print("Handler thread started ID: %d" % int(QtCore.QThread.currentThreadId()))
        self.server.requestProcess.connect(self.process)

    @QtCore.pyqtSlot(str, name='requestProcess')
    def process(self, request: str):
        print("Process handler called")
        response = "None"  # Variable to hold the response to be sent

        if request == "":  # Check if the client is disconnected without any notice
            response = "None"
        elif request == "CONNECT_CLIENT":
            self.client.reConnectSigC.emit()
            response = "Client notified to start"
        elif request == "Test":  # Respond to the connection testing command
            response = "OK"
        elif request == "Terminate":  # Send the required response for the successful termination
            self.log_data.log("INFO", "Client requested connection termination.")
            self.server.releaseClient()
            response = "Bye"
        elif request == "Quit":  # Send the 'Quit' response, which indicates server closing
            response == "Server closing"
        elif request == "Report Position":  # Respond with the current position
            # Add code to calculate and send the current position of the telescope to the client as requested
            response = "POS_0_40_12_34"  # RA_DEC_STPRA_STPDEC
        elif request == "TRKNGSTAT":  # Send the tracking status of the telescope, whether is tracking or not
            response = "NO"  # Value until full functionality is provided
        elif request == "SCALE":  # Send the number of steps per degree for each motor
            response = "SCALEVALS_RA_%d_DEC_%d" % (num_of_stp_per_deg_ra, num_of_stp_per_deg_dec)

        self.server.sendDataClient.emit(response)  # Send the response to the client

    def close(self):
        print("Handler closed")
