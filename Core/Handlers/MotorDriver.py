from PyQt5 import QtCore
import RPi.GPIO as GPIO

HALF_STEPS_ARRAY = [[1, 0], [1, 1], [0, 1], [0, 0]]

# Set the pin numbers where the output is going to be
_RA1_PIN = 11
_RA2_PIN = 13
_DEC1_PIN = 15
_DEC2_PIN = 16
_MOTORS_ENABLE_PIN = 7

# TODO add the values to the settings file and retrieve them when needed. This will be done to avoid problems
RA_STEPS_PER_DEGREE = 43200.0 / 15.0
DEC_STEPS_PER_DEGREE = 10000


class MotorInit(QtCore.QObject):
    def __init__(self, parent=None):
        super(MotorInit, self).__init__(parent)
        # self.gpio_init()  # Initialize the GPIO pins

    # TODO see how the initialization and setting will be implemented for the GPIO (partially complete)
    def gpio_init(self):
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

    def clean_io(self):
        GPIO.cleanup()

    def set_step(self, c_1, c_2, ra_motor):
        if ra_motor:  # If RA_motor is True, then we are talking about the RA motor
            GPIO.output(_RA1_PIN, c_1)
            GPIO.output(_RA2_PIN, c_2)
        else:
            GPIO.output(_DEC1_PIN, c_1)
            GPIO.output(_DEC2_PIN, c_2)

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
    motHaltSig = QtCore.pyqtSignal(name='motionHaltNotifierSignal')  # Signal is emitted when motor stop is requested
    motStartSig = QtCore.pyqtSignal(name='motionStartNotifierSignal')  # Signal is emitted upon motor start up
    trackStatSig = QtCore.pyqtSignal(str, name='trackingStatusSignal')  # Send the tracking status

    def __init__(self, init_ra, init_dec, parent=None):
        super(Stepping, self).__init__(parent)
        self.moveMotSig.connect(self.start)
        self.motor = MotorInit()

        # Initialize all the counter variables
        self.move_ra_count = 0 + int(init_ra)
        self.move_dec_count = 0 + int(init_dec)
        self.temp_ra_count = 0
        self.temp_dec_count = 0
        self.ra_step = 0
        self.dec_step = 0

        self.timer_ra = None
        self.timer_dec = None
        self.ra_moving = False
        self.dec_moving = False
        self.tracking = False  # Tracking indicator

    @QtCore.pyqtSlot(str, name='moveMotorSignal')
    def start(self, command: str):
        if self.motor.motor_status() is True:
            string = command.split("_")  # String format: FRQRA_FRQDEC_STEPRA_STEPDEC
            frq_ra = round(1.0/float(string[0])*1000.0)  # Convert to period given the frequency
            frq_dec = round(1.0/float(string[1])*1000.0)

            try:
                if string[4] == "TRK":
                    self.tracking = True  # Indicate this is a tracking session
            except IndexError:
                self.tracking = False

            # Send the saved steps initially
            self.motStepSig.emit("RASTEPS", self.move_ra_count)
            self.motStepSig.emit("DECSTEPS", self.move_dec_count)

            if frq_ra < 0.0 or frq_dec < 0.0:
                if self.timer_ra is not None:
                    self.timer_ra.stop()
                    self.temp_ra_count = 0
                    self.ra_moving = False
                if self.timer_dec is not None:
                    self.timer_dec.stop()
                    self.temp_dec_count = 0
                    self.dec_moving = False
                self.motStepSig.emit("RASTEPS", self.move_ra_count)  # Send the necessary step updates on stop
                self.motStepSig.emit("DECSTEPS", self.move_dec_count)
                self.updtStepSig.emit(["BOTH", self.move_ra_count, self.move_dec_count])  # Send the total steps
                self.motHaltSig.emit()  # Notify the client that we stopped

                if self.tracking is True:
                    self.trackStatSig.emit("STOPPED")  # Indicate that any tracking has stopped
            else:
                if not self.ra_moving:
                    self.ra_step = int(string[2])  # Get the sent RA steps
                    self.timer_ra = QtCore.QTimer()  # Create the Qt timer object
                    if self.ra_step > 0:  # Forward direction
                        self.timer_ra.timeout.connect(self.move_ra_fwd)
                    else:
                        self.timer_ra.timeout.connect(self.move_ra_back)

                    if self.ra_step != 0:
                        self.ra_moving = True  # Indicate that the motor is moving
                        self.timer_ra.setInterval(frq_ra)
                        self.timer_ra.start()
                        self.motStartSig.emit()
                        if self.tracking is True:
                            self.trackStatSig.emit("STARTED")  # Indicate that tracking has started

                if not self.dec_moving:
                    self.dec_step = int(string[3])  # Get the DEC steps
                    self.timer_dec = QtCore.QTimer()
                    if self.dec_step > 0:
                        self.timer_dec.timeout.connect(self.move_dec_fwd)
                    else:
                        self.timer_dec.timeout.connect(self.move_dec_back)

                    if self.dec_step != 0:
                        self.dec_moving = True
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
        self.motor.set_step(HALF_STEPS_ARRAY[j][0], HALF_STEPS_ARRAY[j][1], True)
        self.move_ra_count = self.move_ra_count + 1  # Hold the total step count
        self.temp_ra_count = self.temp_ra_count + 1  # Temporary step count to know when to stop

        if self.temp_ra_count >= self.ra_step:
            self.timer_ra.stop()  # Stop the timer
            self.timer_ra.timeout.disconnect()  # Disconnect any signals
            self.temp_ra_count = 0  # Reset the temporary step count
            self.ra_moving = False  # Indicate that the motor has now stopped
            if not self.dec_moving:
                self.motStopSig.emit()  # Notify for stopping, if both motors have stopped
                if self.tracking is True:
                    self.trackStatSig.emit("STOPPED")  # Indicate that tracking has stopped

        if self.temp_ra_count % 100 == 0 or self.temp_ra_count >= self.ra_step:
            self.motStepSig.emit("RASTEPS", self.move_ra_count)
            self.updtStepSig.emit(["RA", self.move_ra_count, "0"])

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
        self.motor.set_step(HALF_STEPS_ARRAY[j][0], HALF_STEPS_ARRAY[j][1], False)
        self.move_dec_count = self.move_dec_count + 1
        self.temp_dec_count = self.temp_dec_count + 1

        if self.temp_dec_count >= self.dec_step:
            self.timer_dec.stop()
            self.timer_dec.timeout.disconnect()
            self.temp_dec_count = 0
            self.dec_moving = False
            if not self.ra_moving:
                self.motStopSig.emit()  # Notify for stopping, if both motors have stopped
                if self.tracking is True:
                    self.trackStatSig.emit("STOPPED")  # Indicate that tracking has stopped

        if self.temp_dec_count % 100 == 0 or self.temp_dec_count >= self.dec_step:
            self.motStepSig.emit("DECSTEPS", self.move_dec_count)
            self.updtStepSig.emit(["DEC", "0", self.move_dec_count])

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
        self.motor.set_step(HALF_STEPS_ARRAY[j][0], HALF_STEPS_ARRAY[j][1], True)
        self.move_ra_count = self.move_ra_count - 1
        self.temp_ra_count = self.temp_ra_count + 1

        if self.temp_ra_count >= abs(self.ra_step):
            self.timer_ra.stop()
            self.timer_ra.timeout.disconnect()
            self.temp_ra_count = 0
            self.ra_moving = False
            if not self.dec_moving:
                self.motStopSig.emit()  # Notify for stopping, if both motors have stopped
                if self.tracking is True:
                    self.trackStatSig.emit("STOPPED")  # Indicate that tracking has stopped

        if self.temp_ra_count % 100 == 0 or self.temp_ra_count >= abs(self.ra_step):
            self.motStepSig.emit("RASTEPS", self.move_ra_count)
            self.updtStepSig.emit(["RA", self.move_ra_count, "0"])

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
        self.motor.set_step(HALF_STEPS_ARRAY[j][0], HALF_STEPS_ARRAY[j][1], False)
        self.move_dec_count = self.move_dec_count - 1
        self.temp_dec_count = self.temp_dec_count + 1

        if self.temp_dec_count >= abs(self.dec_step):
            self.timer_dec.stop()
            self.timer_dec.timeout.disconnect()
            self.temp_dec_count = 0
            self.dec_moving = False
            if not self.ra_moving:
                self.motStopSig.emit()  # Notify for stopping, if both motors have stopped
                if self.tracking is True:
                    self.trackStatSig.emit("STOPPED")  # Indicate that tracking has stopped

        if self.temp_dec_count % 100 == 0 or self.temp_dec_count >= abs(self.dec_step):
            self.motStepSig.emit("DECSTEPS", self.move_dec_count)
            self.updtStepSig.emit(["DEC", "0", self.move_dec_count])
