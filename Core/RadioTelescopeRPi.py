#!/usr/bin/env python3

import os
import sys
import logging.config
sys.path.append(os.path.abspath('.'))  # noqa

# pylint: disable=wrong-import-position

# Import the required libraries and classes
from PyQt5 import QtCore
from Position import DishPosition
from Core.Handlers import RequestHandler
from Core.Networking import TCPServer, TCPClient
from Core.Configuration import ConfigDataPi, DefaultData

# pylint: disable=wrong-import-position


def main():
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
        if not os.path.exists('Settings/log_config.ini'):
            print("Logging configuration file not found. Creating the default.", file=sys.stderr)
            log_file = open("Settings/log_config.ini", "w+")  # Open the logging configuration file in writing mode
            log_file.write(DefaultData.LOG_CONFIG_STR)  # Write the default dat to the file
            log_file.close()  # Close the file, since no other operation required
    except Exception as excep:
        print("There is a problem creating the logging configuration file. See tracback: \n%s" % excep, file=sys.stderr)
        sys.exit(-1)  # Exit the program if an error occurred

    # Check if the settings XML file exists
    try:
        if not os.path.exists('Settings/settings_pi.xml'):
            print("Settings file not found. Creating the default.", file=sys.stderr)
            settings_file = open("Settings/settings_pi.xml", "w+")  # Open the settings file in writing mode
            settings_file.write(DefaultData.SETTINGS_XML_STR)  # Write the default dat to the file
            settings_file.close()  # Close the file, since no other operation required
    except Exception as excep:
        print("There is a problem creating the settings file. See tracback: \n%s" % excep, file=sys.stderr)
        sys.exit(-1)  # Exit the program if an error occurred

    logging.config.fileConfig('Settings/log_config.ini')  # Get the and apply the logger configuration
    cfg = ConfigDataPi.ConfDataPi("settings_pi.xml")  # Parse the configuration file and create the object

    app = QtCore.QCoreApplication(sys.argv)  # Create application object

    # Initialize the server
    server = TCPServer.TCPServer(cfg)
    server_thread = QtCore.QThread()
    server.moveToThread(server_thread)
    server_thread.started.connect(server.start)
    # server_thread.finished.connect(server.close)

    # Initialize the client
    client = TCPClient.TCPClient(cfg)
    client_thread = QtCore.QThread()
    client.moveToThread(client_thread)
    client_thread.started.connect(client.start)
    # client_thread.finished.connect(client.close)

    pos_obj = DishPosition.Position(client, cfg)
    pos_thread = QtCore.QThread()
    pos_obj.moveToThread(pos_thread)
    pos_thread.started.connect(pos_obj.start)
    # pos_thread.finished.connect(pos_obj.close)

    # Initialize and start the handler
    request_handle = RequestHandler.RequestHandle(cfg, server, client, pos_obj, server_thread, client_thread,
                                                  pos_thread)
    handler_thread = QtCore.QThread()
    request_handle.moveToThread(handler_thread)
    handler_thread.started.connect(request_handle.start)
    # handler_thread.finished.connect(request_handle.close)
    handler_thread.start()  # Start the handler thread

    sys.exit(app.exec_())  # Start the event loop


if __name__ == '__main__':
    log = logging.getLogger(__name__)  # Create the logger for the program
    try:
        main()  # Start the program
    except Exception:
        log.exception("A general exception occurred. See traceback.")  # Log any exception
