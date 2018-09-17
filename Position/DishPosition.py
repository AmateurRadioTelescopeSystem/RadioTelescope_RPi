from PyQt5 import QtCore
import mpu9250
import logging
import math


class Position(QtCore.QObject):
    def __init__(self, tcpClient, parent=None):
        super(Position, self).__init__(parent)
        self.tcpClient = tcpClient
        self.ra = 1.2
        self.dec = -2.52
        self.ind = 0.5
        self.ra_step_number = 0
        self.dec_step_number = 0
        self.ij = True
        self.log = logging.getLogger(__name__)

    def start(self):
        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(1000)

        try:
            mpu9250.initMPU9250()  # Initialize the MPU sensor
        except:
            self.log.exception("Problem initializing the MPU sensor. See traceback below:")
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

        self.ra = self.ra - 0.05
        if self.ra >= 23.9997:
            self.ra = self.ra - 23.9997
        elif self.ra <= 0.0:
            self.ra = 23.9997 - self.ra
        if type == "RASTEPS":
            self.ra_step_number = steps
        elif type == "DECSTEPS":
            self.dec_step_number = steps
        string = "DISHPOS_RA_%.5f_DEC_%.5f_STEPS_RA_%d_DEC_%d\n" \
                 % (self.ra, self.dec, self.ra_step_number, self.dec_step_number)
        self.tcpClient.sendData.emit(string)

    def getPosition(self):
        # TODO Test the accuracy and reliability of the angle calculations
        acc = mpu9250.readAccelData()  # Get the acceleration data from the sensor
        roll = math.atan2(acc[1], acc[2])  # Calculate roll
        pitch = math.atan2(-acc[0], math.sqrt(acc[1]*acc[1] + acc[2]*acc[2]))  # Calculate pitch
        return [math.degrees(pitch), math.degrees(roll)]  # Roll is the declination and pitch is the hour angle

    '''def close(self):
        print("Dish Pos thread is closing")
        self.timer.stop()
        #self.tcpClient.sendData.emit("Stopped Sending position")
        print("After request")'''
