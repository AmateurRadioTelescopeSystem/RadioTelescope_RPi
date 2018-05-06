from PyQt5 import QtCore
from functools import partial


class Position(QtCore.QObject):
    def __init__(self, tcpClient, parent=None):
        super(Position, self).__init__(parent)
        self.tcpClient = tcpClient

    def start(self):
        print("Dish position thread started ID: %d" % int(QtCore.QThread.currentThreadId()))
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.ra = 11.44341
        self.dec = -37.53793

        self.timer.timeout.connect(self.dataSend)
        self.timer.start()

    def dataSend(self):
        self.ra = self.ra - 0.05
        self.dec = self.dec + 0.05

        string = "DISHPOS_RA_%.5f_DEC_%.5f" % (self.ra, self.dec)
        self.tcpClient.sendData.emit(string)


    def close(self):
        self.timer.stop()
        self.tcpClient.sendData.emit("Stopped Sending position")
