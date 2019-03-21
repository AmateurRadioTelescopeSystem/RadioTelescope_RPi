import logging
from PyQt5 import QtCore, QtNetwork


class TCPServer(QtCore.QObject):
    # Create the signals to be used for data handling
    sendDataClient = QtCore.pyqtSignal(str, name='clientDataSend')  # Send the data to client
    requestProcess = QtCore.pyqtSignal(str, name='requestProcess')  # Send the received data for further processing
    clientDisconnected = QtCore.pyqtSignal(name='cleintDisconnected')  # Report a disconnected client from the server

    def __init__(self, cfg, parent=None):
        super(TCPServer, self).__init__(parent)  # Get the parent of the class
        self.host = cfg.get_host()  # Get the TCP connection host
        self.port = cfg.get_port()  # Get the server port from the settings file
        self.log_data = logging.getLogger(__name__)  # Create the necessary logger

    # This method is called in every thread start
    def start(self):
        """
        This function is called whenever the thread is started. It does the necessary first initializations.
        :return: Nothing
        """
        self.socket = None  # Create the instance os the socket variable to use it later
        self.connect_server()  # Start the server

    def connect_server(self):
        """
        Whenever we want a new TCP connection this function is called.
        :return: Nothing
        """
        if self.host == "localhost":
            self.host = QtNetwork.QHostAddress.LocalHost
        else:
            for ip_address in QtNetwork.QNetworkInterface.allAddresses():
                if ip_address != QtNetwork.QHostAddress.LocalHost and ip_address.toIPv4Address() != 0:
                    break
                else:
                    ip_address = QtNetwork.QHostAddress.LocalHost
            self.host = ip_address  # Save the local IP address

        self.tcp_server = QtNetwork.QTcpServer()  # Create a server object
        self.tcp_server.newConnection.connect(self._new_connection)  # Handler for a new connection
        self.sendDataClient.connect(self.send)  # Connect the signal trigger for data sending

        self.tcp_server.listen(QtNetwork.QHostAddress(self.host), int(self.port))  # Start listening for connections

    # Whenever there is new connection, we call this method
    def _new_connection(self):
        """
        Called whenever there is a new connection.
        :return: Nothing
        """
        if self.tcp_server.hasPendingConnections():
            self.socket = self.tcp_server.nextPendingConnection()  # Returns a new QTcpSocket

            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.socket.readyRead.connect(self._receive)  # If there is pending data get it
                self.socket.disconnected.connect(self._disconnected)  # Execute the appropriate code on state change
                self.socket.error.connect(self._error)  # Log any error occurred
                self.tcp_server.close()  # Stop listening for other connections
                self.log_data.info("Someone connected on server")

    # Should we have data pending to be received, this method is called
    def _receive(self):
        try:
            while self.socket.bytesAvailable() > 0:  # Read all data in que
                rec_data = self.socket.readLine().data().decode('utf-8').rstrip('\n')  # Get the data as a string
                self.requestProcess.emit(rec_data)  # Send the received data to be processed
        except Exception:
            # If data is sent fast, then an exception will occur
            self.log_data.exception("A connected client abruptly disconnected. Returning to connection waiting")

    # If at any moment the connection state is changed, we call this method
    def _disconnected(self):
        # Do the following if the connection is lost
        self.socket.close()
        self.clientDisconnected.emit()
        self.tcp_server.listen(QtNetwork.QHostAddress(self.host), int(self.port))  # Start listening again

    def _error(self):
        self.log_data.warning("Some error occurred in client: %s" % self.socket.errorString())

    # This method is called whenever the signal to send data back is fired
    @QtCore.pyqtSlot(str, name='clientDataSend')
    def send(self, data: str):
        try:
            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.socket.write(data.encode('utf-8'))  # Send data back to client
                self.socket.waitForBytesWritten()  # Wait for the data to be written
        except Exception:
            self.log_data.exception("Problem sending data. See traceback.")

    """
    # This method is called whenever the thread exits
    def close(self):
        print("TCP server thread is closing")
        if self.socket is not None:
            print("Closing server")
            self.socket.disconnected.disconnect()  # Close the disconnect signal first to avoid firing
            self.socket.close()  # Close the underlying TCP socket
        self.tcpServer.close()  # Close the TCP server
        self.sendDataClient.disconnect()  # Detach the signal to avoid any accidental firing (Reconnected at start)
    """
