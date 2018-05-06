#!/usr/bin/env python3.5

# Import the required libraries and classes
from PyQt5 import QtCore
import TCPServer
import TCPClient
import configData_Pi
import requestHandler
import motorDriver
import logData_Pi
import sys

log_data = logData_Pi.logData(__name__)

# TODO Test the functionality of the server and client
# TODO make the app "exitable" so killing is not required for termination


def main():
    cfg = configData_Pi.confDataPi("settings_pi.xml")
    motor = motorDriver.motor()

    motor.GPIO_Init()  # Initialize the GPIO pins on the Raspberry

    app = QtCore.QCoreApplication(sys.argv)
    print("Program started, Main thread ID: %d" % QtCore.QThread.currentThreadId())

    # Initialize the server
    server = TCPServer.TCPServer(cfg)
    serverThread = QtCore.QThread()
    server.moveToThread(serverThread)
    serverThread.started.connect(server.start)
    serverThread.finished.connect(server.close)
    serverThread.start()

    # Initialize the client
    client = TCPClient.TCPClient(cfg)
    clientThread = QtCore.QThread()
    client.moveToThread(clientThread)
    clientThread.started.connect(client.start)
    clientThread.finished.connect(client.close)
    # clientThread.start()

    # Initialize and start the handler
    request_hndl = requestHandler.requestHandle(cfg, server, client)
    handlerThread = QtCore.QThread()
    request_hndl.moveToThread(handlerThread)
    handlerThread.started.connect(request_hndl.start)
    handlerThread.start()  # Start the handler thread

    sys.exit(app.exec_())


if __name__ == '__main__':
    try:
        main()  # Start the program
    except Exception:
        print("A general exception occurred. See the log file for details.")
        log_data.log("EXCEPT", "A general exception occurred. See traceback.")  # Log any exception
