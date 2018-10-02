from PyQt5 import QtCore
import RPi.GPIO as GPIO

_steps_half = [[1, 0], [1, 1], [0, 1], [0, 0]]

# Set the pin numbers where the output is going to be
_RA1_PIN = 11
_RA2_PIN = 13
_DEC1_PIN = 15
_DEC2_PIN = 16
_MOTORS_ENABLE_PIN = 7

# TODO add the values to the settings file and retrieve them when needed. This will be done to avoid problems
ra_steps_per_deg = 43200.0 / 15.0
dec_steps_per_deg = 10000


class MotorInit(QtCore.QObject):
    def __init__(self, parent=None):
        super(MotorInit, self).__init__(parent)
        # self.GPIO_Init()  # Initialize the GPIO pins

    # TODO see how the initialization and setting will be implemented for the GPIO (partially complete)
    def GPIO_Init(self):
        # Set the pin numbering mode
        GPIO.setmode(GPIO.BOARD)

        # Setup the output pins
        GPIO.setup(_RA1_PIN, GPIO.OUT)
        GPIO.setup(_RA2_PIN, GPIO.OUT)
        GPIO.setup(_DEC1_PIN, GPIO.OUT)
        GPIO.setup(_DEC2_PIN, GPIO.OUT)
        GPIO.setup(_MOTORS_ENABLE_PIN, GPIO.OUT)

        # Set the pins to LOW for the initial setup
        GPIO.output(_RA1_PIN, 0)
        GPIO.output(_RA2_PIN, 0)
        GPIO.output(_DEC1_PIN, 0)
        GPIO.output(_DEC2_PIN, 0)
        GPIO.output(_MOTORS_ENABLE_PIN, 1)  # Set to HIGH as needed by the switch

    def clean_IO(self):
        GPIO.cleanup()

    def setStep(self, c1, c2, RA_motor):
        if RA_motor:  # If RA_motor is True, then we are talking about the RA motor
            GPIO.output(_RA1_PIN, c1)
            GPIO.output(_RA2_PIN, c2)
        else:
            GPIO.output(_DEC1_PIN, c1)
            GPIO.output(_DEC2_PIN, c2)

    def enabler(self, enable: bool):
        if enable:
            GPIO.output(_MOTORS_ENABLE_PIN, 0)  # Set to LOW to change the relay switch
        else:
            GPIO.output(_MOTORS_ENABLE_PIN, 1)  # Set to high to let switch fall to default position

    def motor_status(self):
        return not GPIO.input(_MOTORS_ENABLE_PIN)  # We have inverted logic in enabling/disabling


class Stepping(QtCore.QObject):
    moveMotSig = QtCore.pyqtSignal(str, name='moveMotorSignal')  # Signal triggered when motor move is desired
    motStepSig = QtCore.pyqtSignal(str, int, name='motorStepCount')  # Triggered when step count is sent
    updtStepSig = QtCore.pyqtSignal(list, name='updateSteps')  # Update the steps signal
    motStopSig = QtCore.pyqtSignal(name='motionStopNotifierSignal')  # Signal is emitted when the motors stop
    motStartSig = QtCore.pyqtSignal(name='motionStartNotifierSignal')  # Signal is emitted upon motor start up
    trackStatSig = QtCore.pyqtSignal(str, name='trackingStatusSignal')  # Send the tracking status

    def __init__(self, init_ra, init_dec, parent=None):
        super(Stepping, self).__init__(parent)
        self.moveMotSig.connect(self.start)
        self.motor = MotorInit()

        # Initialize all the counter variables
        self.moveRaCount = 0 + int(init_ra)
        self.moveDecCount = 0 + int(init_dec)
        self.tempRaCount = 0
        self.tempDecCount = 0
        self.ra_step = 0
        self.dec_step = 0

        self.timer_ra = None
        self.timer_dec = None
        self.raMoving = False
        self.decMoving = False
        self.tracking = False  # Tracking indicator

    @QtCore.pyqtSlot(str, name='moveMotorSignal')
    def start(self, set: str):
        if self.motor.motor_status() is True:
            string = set.split("_")  # String format: FRQRA_FRQDEC_STEPRA_STEPDEC
            frq_ra = round(1.0/float(string[0])*1000.0)  # Convert to period given the frequency
            frq_dec = round(1.0/float(string[1])*1000.0)

            try:
                if string[4] == "TRK":
                    self.tracking = True  # Indicate this is a tracking session
            except IndexError:
                self.tracking = False

            # Send the saved steps initially
            self.motStepSig.emit("RASTEPS", self.moveRaCount)
            self.motStepSig.emit("DECSTEPS", self.moveDecCount)

            if frq_ra < 0.0 or frq_dec < 0.0:
                if self.timer_ra is not None:
                    self.timer_ra.stop()
                    self.tempRaCount = 0
                    self.raMoving = False
                if self.timer_dec is not None:
                    self.timer_dec.stop()
                    self.tempDecCount = 0
                    self.decMoving = False
                self.motStepSig.emit("RASTEPS", self.moveRaCount)  # Send the necessary step updates on stop
                self.motStepSig.emit("DECSTEPS", self.moveDecCount)
                self.updtStepSig.emit(["BOTH", self.moveRaCount, self.moveDecCount])  # Send the total steps
                self.motStopSig.emit()  # Notify the client that we stopped

                if self.tracking is True:
                    self.trackStatSig.emit("STOPPED")  # Indicate that any tracking has stopped
            else:
                if not self.raMoving:
                    self.ra_step = int(string[2])  # Get the sent RA steps
                    self.timer_ra = QtCore.QTimer()  # Create the Qt timer object
                    if self.ra_step > 0:  # Forward direction
                        self.timer_ra.timeout.connect(self.move_ra_fwd)
                    else:
                        self.timer_ra.timeout.connect(self.move_ra_back)

                    if self.ra_step != 0:
                        self.raMoving = True  # Indicate that the motor is moving
                        self.timer_ra.setInterval(frq_ra)
                        self.timer_ra.start()
                        self.motStartSig.emit()
                        if self.tracking is True:
                            self.trackStatSig.emit("STARTED")  # Indicate that tracking has started

                if not self.decMoving:
                    self.dec_step = int(string[3])  # Get the DEC steps
                    self.timer_dec = QtCore.QTimer()
                    if self.dec_step > 0:
                        self.timer_dec.timeout.connect(self.move_dec_fwd)
                    else:
                        self.timer_dec.timeout.connect(self.move_dec_back)

                    if self.dec_step != 0:
                        self.decMoving = True
                        self.timer_dec.setInterval(frq_dec)
                        self.timer_dec.start()
                        self.motStartSig.emit()
                        if self.tracking is True:
                            self.trackStatSig.emit("STARTED")  # Indicate that tracking has started

    def move_ra_fwd(self):
        j = 0  # Initialize the local variable
        if (not GPIO.input(_RA1_PIN)) and (not GPIO.input(_RA2_PIN)):  # If both pins are off
            j = 0  # Set the variable to the next state
        elif GPIO.input(_RA1_PIN) and GPIO.input(_RA2_PIN):  # If just one pin is on
            j = 2
        elif GPIO.input(_RA1_PIN) and (not GPIO.input(_RA2_PIN)):
            j = 1
        elif not GPIO.input(_RA1_PIN) and GPIO.input(_RA2_PIN):
            j = 3
        self.motor.setStep(_steps_half[j][0], _steps_half[j][1], True)
        self.moveRaCount = self.moveRaCount + 1  # Hold the total step count
        self.tempRaCount = self.tempRaCount + 1  # Temporary step count to know when to stop

        if self.tempRaCount >= self.ra_step:
            self.timer_ra.stop()  # Stop the timer
            self.timer_ra.timeout.disconnect()  # Disconnect any signals
            self.tempRaCount = 0  # Reset the temporary step count
            self.raMoving = False  # Indicate that the motor has now stopped
            if not self.decMoving:
                self.motStopSig.emit()  # Notify for stopping, if both motors have stopped
                if self.tracking is True:
                    self.trackStatSig.emit("STOPPED")  # Indicate that tracking has stopped

        if self.tempRaCount % 100 == 0 or self.tempRaCount >= self.ra_step:
            self.motStepSig.emit("RASTEPS", self.moveRaCount)
            self.updtStepSig.emit(["RA", self.moveRaCount, "0"])

    def move_dec_fwd(self):
        j = 0
        if (not GPIO.input(_DEC1_PIN)) and (not GPIO.input(_DEC2_PIN)):  # If both pins are off
            j = 0  # Set the variable to the next state
        elif GPIO.input(_DEC1_PIN) and GPIO.input(_DEC2_PIN):  # If just one pin is on
            j = 2
        elif GPIO.input(_DEC1_PIN) and (not GPIO.input(_DEC2_PIN)):
            j = 1
        elif not GPIO.input(_DEC1_PIN) and GPIO.input(_DEC2_PIN):
            j = 3
        self.motor.setStep(_steps_half[j][0], _steps_half[j][1], False)
        self.moveDecCount = self.moveDecCount + 1
        self.tempDecCount = self.tempDecCount + 1

        if self.tempDecCount >= self.dec_step:
            self.timer_dec.stop()
            self.timer_dec.timeout.disconnect()
            self.tempDecCount = 0
            self.decMoving = False
            if not self.raMoving:
                self.motStopSig.emit()  # Notify for stopping, if both motors have stopped
                if self.tracking is True:
                    self.trackStatSig.emit("STOPPED")  # Indicate that tracking has stopped

        if self.tempDecCount % 100 == 0 or self.tempDecCount >= self.dec_step:
            self.motStepSig.emit("DECSTEPS", self.moveDecCount)
            self.updtStepSig.emit(["DEC", "0", self.moveDecCount])

    def move_ra_back(self):
        j = 0
        if (not GPIO.input(_RA1_PIN)) and (not GPIO.input(_RA2_PIN)):  # If both pins are off
            j = 2  # Set the variable to the next state
        elif GPIO.input(_RA1_PIN) and GPIO.input(_RA2_PIN):  # If just one pin is on
            j = 0
        elif GPIO.input(_RA1_PIN) and (not GPIO.input(_RA2_PIN)):
            j = 3
        elif not GPIO.input(_RA1_PIN) and GPIO.input(_RA2_PIN):
            j = 1
        self.motor.setStep(_steps_half[j][0], _steps_half[j][1], True)
        self.moveRaCount = self.moveRaCount - 1
        self.tempRaCount = self.tempRaCount + 1

        if self.tempRaCount >= abs(self.ra_step):
            self.timer_ra.stop()
            self.timer_ra.timeout.disconnect()
            self.tempRaCount = 0
            self.raMoving = False
            if not self.decMoving:
                self.motStopSig.emit()  # Notify for stopping, if both motors have stopped
                if self.tracking is True:
                    self.trackStatSig.emit("STOPPED")  # Indicate that tracking has stopped

        if self.tempRaCount % 100 == 0 or self.tempRaCount >= abs(self.ra_step):
            self.motStepSig.emit("RASTEPS", self.moveRaCount)
            self.updtStepSig.emit(["RA", self.moveRaCount, "0"])

    def move_dec_back(self):
        j = 0
        if (not GPIO.input(_DEC1_PIN)) and (not GPIO.input(_DEC2_PIN)):  # If both pins are off
            j = 2  # Set the variable to the next state
        elif GPIO.input(_DEC1_PIN) and GPIO.input(_DEC2_PIN):  # If just one pin is on
            j = 0
        elif GPIO.input(_DEC1_PIN) and (not GPIO.input(_DEC2_PIN)):
            j = 3
        elif not GPIO.input(_DEC1_PIN) and GPIO.input(_DEC2_PIN):
            j = 1
        self.motor.setStep(_steps_half[j][0], _steps_half[j][1], False)
        self.moveDecCount = self.moveDecCount - 1
        self.tempDecCount = self.tempDecCount + 1

        if self.tempDecCount >= abs(self.dec_step):
            self.timer_dec.stop()
            self.timer_dec.timeout.disconnect()
            self.tempDecCount = 0
            self.decMoving = False
            if not self.raMoving:
                self.motStopSig.emit()  # Notify for stopping, if both motors have stopped
                if self.tracking is True:
                    self.trackStatSig.emit("STOPPED")  # Indicate that tracking has stopped

        if self.tempDecCount % 100 == 0 or self.tempDecCount >= abs(self.dec_step):
            self.motStepSig.emit("DECSTEPS", self.moveDecCount)
            self.updtStepSig.emit(["DEC", "0", self.moveDecCount])
