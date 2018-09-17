from PyQt5 import QtCore


class Position(QtCore.QObject):
    def __init__(self, tcpClient, parent=None):
        super(Position, self).__init__(parent)
        self.tcpClient = tcpClient
        self.ra = 1.2
        # self.dec = -37.53793
        self.dec = -2.52
        self.ind = 0.5
        self.ra_step_number = 0
        self.dec_step_number = 0
        self.ij = True

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)

        # self.timer.timeout.connect(self.dataSend)
        # self.timer.start()

    @QtCore.pyqtSlot(str, int, name='motorStepCount')
    def dataSend(self, type: str, steps: int):
        if self.ij:
            print("Dish position thread: %d" % int(QtCore.QThread.currentThreadId()))
            self.ij = False
        self.ind = self.ind - 0.005
        '''if self.dec >= 90.0 or self.dec <= -90.0:
            self.dec = self.dec - self.ind
        else:
            self.dec = self.dec + self.ind'''
        '''self.ra = self.ra + self.ind
        self.dec = self.dec + self.ind

        if self.dec >= 90.0:
            self.dec = self.dec - 90.0
        elif self.dec <= -90.0:
            self.dec = 90.0 - self.dec'''

        self.ra = self.ra -0.005
        if self.ra >= 24.0:
            self.ra = self.ra - 24.0
        elif self.ra <= 0.0:
            self.ra = 24.0 - self.ra
        if type == "RASTEPS":
            self.ra_step_number = steps
        elif type == "DECSTEPS":
            self.dec_step_number = steps
        string = "DISHPOS_RA_%.5f_DEC_%.5f_STEPS_RA_%d_DEC_%d\n" \
                 % (self.ra, self.dec, self.ra_step_number, self.dec_step_number)
        self.tcpClient.sendData.emit(string)

    def getPosition(self):
        return [self.ra, self.dec]

    '''def close(self):
        print("Dish Pos thread is closing")
        self.timer.stop()
        #self.tcpClient.sendData.emit("Stopped Sending position")
        print("After request")'''
