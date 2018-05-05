#!/usr/bin/env python3.5

# Import the required libraries and classes
from PyQt5 import QtCore
import TCPServer
import configData_Pi
import requestHandler
import motorDriver
import logData_Pi
import sys


def main():
    cfg = configData_Pi.confDataPi("settings_pi.xml")
    request_hndl = requestHandler.requestHandle(cfg)
    log_data = logData_Pi.logData(__name__)
    motor = motorDriver.motor()

    motor.GPIO_Init()  # Initialize the GPIO pins on the Raspberry

    app = QtCore.QCoreApplication(sys.argv)
    print("Program started, Main thread ID: %d" % QtCore.QThread.currentThreadId())

    server = TCPServer.TCPServer(cfg)
    serverThread = QtCore.QThread()
    server.moveToThread(serverThread)
    serverThread.started.connect(server.start)
    serverThread.finished.connect(server.close)
    serverThread.start()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
