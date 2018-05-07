from PyQt5 import QtCore


class Position(QtCore.QObject):
    def __init__(self, tcpClient, parent=None):
        super(Position, self).__init__(parent)
        self.tcpClient = tcpClient
        self.ra = 11.44341
        # self.dec = -37.53793
        self.dec = -2.0
        self.ind = 0.5

    def start(self):
        print("Dish position thread started ID: %d" % int(QtCore.QThread.currentThreadId()))
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)

        self.timer.timeout.connect(self.dataSend)
        self.timer.start()

    def dataSend(self):
        '''if self.dec >= 90.0 or self.dec <= -90.0:
            self.dec = self.dec - self.ind
        else:
            self.dec = self.dec + self.ind'''
        '''self.ra = self.ra + self.ind
        self.dec = self.dec + self.ind

        if self.dec >= 90.0:
            self.dec = self.dec - 90.0
        elif self.dec <= -90.0:
            self.dec = 90.0 - self.dec

        if self.ra >= 24.0:
            self.ra = self.ra - 24.0
        elif self.ra <= 0.0:
            self.ra = 24.0 - self.ra'''

        string = "DISHPOS_RA_%.5f_DEC_%.5f\n" % (self.ra, self.dec)
        self.tcpClient.sendData.emit(string)

    def getPosition(self):
        return [self.ra, self.dec]

    '''def close(self):
        print("Dish Pos thread is closing")
        self.timer.stop()
        #self.tcpClient.sendData.emit("Stopped Sending position")
        print("After request")'''
