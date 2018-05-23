from PyQt5 import QtCore
import RPi.GPIO as GPIO
from functools import partial
import threading
import time

_steps_half = [[1, 0], [1, 1], [0, 1], [0, 0]]

# Set the pin numbers where the output is going to be
_RA1_PIN = 7
_RA2_PIN = 8
_DEC1_PIN = 10
_DEC2_PIN = 12


class MotorInit(QtCore.QObject):
    def __init__(self, parent=None):
        super(MotorInit, self).__init__(parent)
        print("MotorInit constructor thread ID: %d" % QtCore.QThread.currentThreadId())
        # self.GPIO_Init()  # Initialize the GPIO pins

    # TODO see how the initialization and setting will be implemented for the GPIO
    def GPIO_Init(self):
        # Set the pin numbering mode
        GPIO.setmode(GPIO.BOARD)

        # Setup the output pins
        GPIO.setup(_RA1_PIN, GPIO.OUT)
        GPIO.setup(_RA2_PIN, GPIO.OUT)
        GPIO.setup(_DEC1_PIN, GPIO.OUT)
        GPIO.setup(_DEC2_PIN, GPIO.OUT)

        # Set the pins to LOW for the initial setup
        GPIO.output(_RA1_PIN, 0)
        GPIO.output(_RA2_PIN, 0)
        GPIO.output(_DEC1_PIN, 0)
        GPIO.output(_DEC2_PIN, 0)

    def clean_IO(self):
        GPIO.cleanup()

    def setStep(self, c1, c2, RA_motor):
        if RA_motor:  # If RA_motor is True, then we are talking about the RA motor
            GPIO.output(_RA1_PIN, c1)
            GPIO.output(_RA2_PIN, c2)
        else:
            GPIO.output(_DEC1_PIN, c1)
            GPIO.output(_DEC2_PIN, c2)


# TODO implement the time delay for the stepping using a QTimer
# TODO test with LEDs how it functions
class Stepping(QtCore.QObject):
    moveMotSig = QtCore.pyqtSignal(str, name='moveMotorSignal')  # Signal triggered when motor move is desired
    motStepSig = QtCore.pyqtSignal(str, int, name='motorStepCount')  # Triggered when step count is sent
    updtStepSig = QtCore.pyqtSignal(list, name='updateSteps')

    def __init__(self, parent=None):
        super(Stepping, self).__init__(parent)
        print("Stepping constructor thread ID: %d" % QtCore.QThread.currentThreadId())
        self.moveMotSig.connect(self.start)
        self.motor = MotorInit()

        # Initialize all the counter variables
        self.moveRaCount = 0
        self.moveDecCount = 0
        self.tempRaCount = 0
        self.tempDecCount = 0

        self.timer_ra = None
        self.timer_dec = None
        self.raMoving = False
        self.decMoving = False

    @QtCore.pyqtSlot(str, name='moveMotorSignal')
    def start(self, set: str):
        string = set.split("_")  # String format: FRQRA_FRQDEC_STEPRA_STEPDEC
        frq_ra = round(1.0/float(string[0])*1000.0)  # Convert to period given the frequency
        frq_dec = round(1.0/float(string[1])*1000.0)

        if frq_ra < 0.0 or frq_dec < 0.0:
            if self.timer_ra is not None:
                self.timer_ra.stop()
                self.tempRaCount = 0
                self.raMoving = False
            if self.timer_dec is not None:
                self.timer_dec.stop()
                self.tempDecCount = 0
                self.decMoving = False
        else:
            if not self.raMoving:
                self.ra_step = int(string[2])  # Get the sent RA steps
                self.timer_ra = QtCore.QTimer()
                if self.ra_step > 0:  # Forward direction
                    self.timer_ra.timeout.connect(self.move_ra_fwd)
                else:
                    self.timer_ra.timeout.connect(self.move_ra_back)

                if self.ra_step != 0:
                    self.raMoving = True  # Indicate that the motor is moving
                    self.timer_ra.setInterval(frq_ra)
                    self.timer_ra.start()

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

        if self.tempRaCount%10 == 0 or self.tempRaCount >= self.ra_step:
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

        if self.tempDecCount%10 == 0 or self.tempDecCount >= self.dec_step:
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

        if self.tempRaCount%10 == 0 or self.tempRaCount >= abs(self.ra_step):
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

        if self.tempDecCount%10 == 0 or self.tempDecCount >= abs(self.dec_step):
            self.motStepSig.emit("DECSTEPS", self.moveDecCount)
            self.updtStepSig.emit(["DEC", "0", self.moveDecCount])
