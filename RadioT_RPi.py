#!/usr/bin/env python3.5

# Import the required libraries and classes
from PyQt5 import QtCore
from Networking import TCPClient, TCPServer
import configData_Pi
import requestHandler
import logging.config
import sys
import os
from Position import DishPosition
import defaultData


# TODO Test the functionality of the server and client
# TODO make the app "exitable" so killing is not required for termination

# Create the directory for the log files if it does not exist already
try:
    if not os.path.exists('logs'):
        os.makedirs('logs')
except Exception as excep:
    print("There is a problem with the log directory. See tracback: \n%s" % excep, file=sys.stderr)
    sys.exit(-1)  # Exit the program if an error occurred

# Check if the logging configuration file exists
try:
    if not os.path.exists('log_config.ini'):
        print("Logging configuration file not found. Creating the default.")
        log_file = open("log_config.ini", "w+")  # Open the logging configuration file in writing mode
        log_file.write(defaultData.log_config_str)  # Write the default dat to the file
        log_file.close()  # Close the file, since no other operation required
except Exception as excep:
    print("There is a problem creating the logging configuration file. See tracback: \n%s" % excep, file=sys.stderr)
    sys.exit(-1)  # Exit the program if an error occurred

# Check if the settings XML file exists
try:
    if not os.path.exists('settings_pi.xml'):
        print("Settings file not found. Creating the default.")
        setngs_file = open("settings_pi.xml", "w+")  # Open the settings file in writing mode
        setngs_file.write(defaultData.settings_xml_str)  # Write the default dat to the file
        setngs_file.close()  # Close the file, since no other operation required
except Exception as excep:
    print("There is a problem creating the settings file. See tracback: \n%s" % excep, file=sys.stderr)
    sys.exit(-1)  # Exit the program if an error occurred

log_data = logging.config.fileConfig('log_config.ini')  # Get the and apply the logger configuration


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
        log.exception("A general exception occurred. See traceback.")  # Log any exception
