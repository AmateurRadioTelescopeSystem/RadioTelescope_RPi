from PyQt5 import QtCore, QtNetwork
import logging


class TCPClient(QtCore.QObject):
    # Create the signals to be used for data handling
    dataRcvSigC = QtCore.pyqtSignal(str, name='dataClientRX')  # Send the received data out
    sendData = QtCore.pyqtSignal(str, name='sendDataClient')  # Data to be sent to the server
    reConnectSigC = QtCore.pyqtSignal(name='reConnectClient')  # A reconnection signal originating from a button press

    def __init__(self, cfgData, parent=None):
        super(TCPClient, self).__init__(parent)  # Get the parent of the class
        self.cfgData = cfgData  # Create a variable for the cfg file

    def start(self):
        print("Client thread: %d" % int(QtCore.QThread.currentThreadId()))
        self.log_data = logging.getLogger(__name__)  # Create the logger
        self.sock = QtNetwork.QTcpSocket()  # Create the TCP socket
        self.reConnectSigC.connect(self.connect)  # Do the reconnect signal connection
        self.connect()  # Start a connection

    # The connect function is called if the signal is fired or in the start of the thread
    @QtCore.pyqtSlot(name='reConnectClient')
    def connect(self):
        if self.sock.state() != QtNetwork.QAbstractSocket.ConnectedState:
            # Get the host and port from the settings file for the client connection
            host = self.cfgData.getClientHost()
            port = self.cfgData.getClientPort()

            self.sock = QtNetwork.QTcpSocket()  # Create the TCP socket
            self.sock.readyRead.connect(self._receive)  # Data que signal
            self.sock.connected.connect(self._hostConnected)  # What to do when we have connected
            self.sock.error.connect(self._error)  # Log any error occurred and also perform the necessary actions
            self.sock.disconnected.connect(self._disconnected)  # If there is state change then call the function

            self.sock.connectToHost(QtNetwork.QHostAddress(host), int(port))  # Attempt to connect to the server

            self.sock.waitForConnected(msecs=1000)  # Wait a until connected (the function is waiting for 1 sec)

    @QtCore.pyqtSlot(str, name='sendDataClient')
    def sendD(self, data: str):
        if self.sock.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.sock.write(data.encode('utf-8'))
            self.sock.waitForBytesWritten()

    def _receive(self):
        while self.sock.bytesAvailable() > 0:  # Read all data in que
            string = self.sock.readLine().data().decode('utf-8').rstrip('\n')  # Get the data as a string
            self.sock.readLine()
            self.dataRcvSigC.emit(string)  # Decode the data to a string

    def _disconnected(self):
        self.sendData.disconnect()
        self.sock.waitForConnected(msecs=1000)

    def _hostConnected(self):
        self.sendData.connect(self.sendD)  # Send the data to the server when this signal is fired

    def _error(self):
        self.log_data.warning("Some error occurred in client: %s" % self.sock.errorString())

    ''''# This method is called when the thread exits
    def close(self):
        print("TCP client thread is closing")
        self.sock.disconnected.disconnect()  # Disconnect this signal first to avoid getting in the function
        if self.sock.state() == QtNetwork.QAbstractSocket.ConnectedState:
            self.sendData.disconnect(self.sendD)  # Disconnect the data send signal, since the thread is closing
            self.sock.disconnectFromHost()  # Disconnect from the host
            self.sock.waitForDisconnected(msecs=1000)  # And wait until disconnected or timeout (default 3 seconds)
        else:
            self.sock.close()  # Close the socket before exiting
        self.reConnectSigC.disconnect()  # Thread is closing so it will not be needed any more'''
