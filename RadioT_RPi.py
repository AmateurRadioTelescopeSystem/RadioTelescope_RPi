#!/usr/bin/env python3.5

# Import the required libraries and classes
from PyQt5 import QtCore
from Networking import TCPClient, TCPServer
import configData_Pi
import requestHandler
import logging
import logging.config
import sys
import DishPosition

log_data = logging.config.fileConfig('log_config.ini')  # Get the and apply the logger configuration

# TODO Test the functionality of the server and client
# TODO make the app "exitable" so killing is not required for termination


def main():
    cfg = configData_Pi.confDataPi("settings_pi.xml")

    app = QtCore.QCoreApplication(sys.argv)
    print("Program started, Main thread ID: %d" % QtCore.QThread.currentThreadId())

    # Initialize the server
    server = TCPServer.TCPServer(cfg)
    serverThread = QtCore.QThread()
    server.moveToThread(serverThread)
    serverThread.started.connect(server.start)
    #serverThread.finished.connect(server.close)

    # Initialize the client
    client = TCPClient.TCPClient(cfg)
    clientThread = QtCore.QThread()
    client.moveToThread(clientThread)
    clientThread.started.connect(client.start)
    #clientThread.finished.connect(client.close)

    posObj = DishPosition.Position(client)
    posThread = QtCore.QThread()
    posObj.moveToThread(posThread)
    posThread.started.connect(posObj.start)
    #posThread.finished.connect(posObj.close)

    # Initialize and start the handler
    request_hndl = requestHandler.requestHandle(cfg, server, client, posObj, serverThread, clientThread, posThread)
    handlerThread = QtCore.QThread()
    request_hndl.moveToThread(handlerThread)
    handlerThread.started.connect(request_hndl.start)
    #handlerThread.finished.connect(request_hndl.close)
    handlerThread.start()  # Start the handler thread

    sys.exit(app.exec_())  # Start the event loop


if __name__ == '__main__':
    log = logging.getLogger(__name__)  # Create the logger for the program
    try:
        main()  # Start the program
    except Exception:
        print("A general exception occurred. See the log file for details.")
        log.exception("A general exception occurred. See traceback.")  # Log any exception
