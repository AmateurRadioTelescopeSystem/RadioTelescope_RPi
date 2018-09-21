from PyQt5 import QtCore
import mpu9250
import logging
import math


class Position(QtCore.QObject):
    def __init__(self, tcpClient, cfg_data, parent=None):
        super(Position, self).__init__(parent)
        self.tcpClient = tcpClient
        self.cfg = cfg_data
        self.ra = 0
        self.dec = 0

        # Initialize the steps upon the creation of this class
        steps = cfg_data.getSteps()
        self.ra_step_number = steps[0]
        self.dec_step_number = steps[1]

        self.log = logging.getLogger(__name__)  # Initialize the logger

    def start(self):
        # self.timer = QtCore.QTimer()
        # self.timer.setInterval(1000)
        print("Position thread started")

        '''
        try:
            mpu9250.initMPU9250()  # Initialize the MPU sensor
        except:
            self.log.exception("Problem initializing the MPU sensor. See traceback below:")
        '''
        # self.timer.timeout.connect(self.dataSend)
        # self.timer.start()

    @QtCore.pyqtSlot(str, int, name='motorStepCount')
    def dataSend(self, type: str, steps: int):
        """
        Sends position information alongside with the step number.
        :param type: What is the motor that is triggering this signal
        :param steps: Number of steps sent from the signal trigger
        :return: Nothing
        """
        posit = self.getPosition()
        self.ra = posit[0]
        self.dec = posit[1]

        if type == "RASTEPS":
            self.ra_step_number = steps
        elif type == "DECSTEPS":
            self.dec_step_number = steps
        string = "DISHPOS_RA_%.5f_DEC_%.5f_STEPS_RA_%d_DEC_%d\n" \
                 % (self.ra, self.dec, self.ra_step_number, self.dec_step_number)
        self.tcpClient.sendData.emit(string)

    def getPosition(self):
        # TODO Test the accuracy and reliability of the angle calculations
        '''
        acc = mpu9250.readAccelData()  # Get the acceleration data from the sensor
        roll = math.atan2(acc[1], acc[2])  # Calculate roll
        pitch = math.atan2(-acc[0], math.sqrt(acc[1]*acc[1] + acc[2]*acc[2]))  # Calculate pitch
        return [math.degrees(pitch), math.degrees(roll)]  # Roll is the declination and pitch is the hour angle
        '''
        stps = self.cfg.getSteps()
        ha = float(stps[0])/43200.0
        dec = float(stps[1])/10000.0
        
        if ha < 0.0:
            ha = 23.9997 - abs(ha)
        elif ha >= 23.997:
            ha = ha - 23.997
        return [float(ha), float(dec)]

    '''def close(self):
        print("Dish Pos thread is closing")
        self.timer.stop()
        #self.tcpClient.sendData.emit("Stopped Sending position")
        print("After request")'''
