from PyQt5 import QtCore, QtNetwork
import logData_Pi


class TCPServer(QtCore.QObject):
    # Create the signals to be used for data handling
    sendDataClient = QtCore.pyqtSignal(str, name='clientDataSend')  # Send the data to client
    requestProcess = QtCore.pyqtSignal(str, name='requestProcess')  # Send the received data for further processing

    def __init__(self, cfg, parent=None):
        super(TCPServer, self).__init__(parent)  # Get the parent of the class
        self.host = cfg.getHost()  # Get the TCP connection host
        self.port = cfg.getPort()  # Get the server port from the settings file
        self.log_data = logData_Pi.logData(__name__)  # Create the necessary logger

    # This method is called in every thread start
    def start(self):
        print("Server thread started ID: %d" % int(QtCore.QThread.currentThreadId()))
        self.socket = None  # Create the instance os the socket variable to use it later
        self.connectServ()  # Start the server

    def connectServ(self):
        if self.host == "localhost":
            self.host = QtNetwork.QHostAddress.LocalHost
        else:
            for ipAddress in QtNetwork.QNetworkInterface.allAddresses():
                if ipAddress != QtNetwork.QHostAddress.LocalHost and ipAddress.toIPv4Address() != 0:
                    break
                else:
                    ipAddress = QtNetwork.QHostAddress.LocalHost
            self.host = ipAddress  # Save the local IP address

        self.tcpServer = QtNetwork.QTcpServer()  # Create a server object
        self.tcpServer.newConnection.connect(self._new_connection)  # Handler for a new connection
        self.sendDataClient.connect(self.send)  # Connect the signal trigger for data sending

        self.tcpServer.listen(QtNetwork.QHostAddress(self.host), int(self.port))  # Start listening for connections

    # Whenever there is new connection, we call this method
    def _new_connection(self):
        if self.tcpServer.hasPendingConnections():
            self.socket = self.tcpServer.nextPendingConnection()  # Returns a new QTcpSocket

            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.socket.readyRead.connect(self._receive)  # If there is pending data get it
                self.socket.disconnected.connect(self._disconnected)  # Execute the appropriate code on state change
                self.tcpServer.close()  # Stop listening for other connections
                print("We have new connection")

    # Should we have data pending to be received, this method is called
    def _receive(self):
        try:
            while self.socket.bytesAvailable() > 0:  # Read all data in que
                recData = self.socket.readLine().data().decode('utf-8').rstrip('\n')  # Get the data as a string
                self.requestProcess.emit(recData)  # Send the received data to be processed
                print("The received data is (Server here): %s" % recData)
        except Exception:
            # If data is sent fast, then an exception will occur
            self.log_data.log("EXCEPT", "A connected client abruptly disconnected. Returning to connection waiting")

    # If at any moment the connection state is changed, we call this method
    def _disconnected(self):
        # Do the following if the connection is lost
        self.socket.close()
        self.tcpServer.listen(QtNetwork.QHostAddress(self.host), int(self.port))  # Start listening again

    # This method is called whenever the signal to send data back is fired
    @QtCore.pyqtSlot(str, name='clientDataSend')
    def send(self, data: str):
        try:
            if self.socket.state() == QtNetwork.QAbstractSocket.ConnectedState:
                self.socket.write(data.encode('utf-8'))  # Send data back to client
                self.socket.waitForBytesWritten()  # Wait for the data to be written
                # print("Those were sent: %s" % data)
        except Exception:
            self.log_data.log("EXCEPT", "Problem sending data. See traceback.")

    ''''# This method is called whenever the thread exits
    def close(self):
        print("TCP server thread is closing")
        if self.socket is not None:
            print("Closing server")
            self.socket.disconnected.disconnect()  # Close the disconnect signal first to avoid firing
            self.socket.close()  # Close the underlying TCP socket
        self.tcpServer.close()  # Close the TCP server
        self.sendDataClient.disconnect()  # Detach the signal to avoid any accidental firing (Reconnected at start)'''
