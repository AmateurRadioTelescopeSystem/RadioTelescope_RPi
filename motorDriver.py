from PyQt5 import QtCore
import RPi.GPIO as GPIO
import threading
import time

_steps_half = [[1, 0], [1, 1], [0, 1]]

# Set the pin numbers where the output is going to be
_RA1_PIN = 7
_RA2_PIN = 8
_DEC1_PIN = 10
_DEC2_PIN = 12

# TODO make the class a a QObject, so we can use QThreads to take advantage of signals and slots


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
            GPIO.output(_DEC2_PIN, c1)
            GPIO.output(_DEC2_PIN, c2)


# TODO implement the time delay for the stepping using a QTimer
# TODO test with LEDs how it functions
class SteppingFwd(QtCore.QObject):
    def __init__(self, parent=None):
        super(SteppingFwd, self).__init__(parent)
        print("SteppingFwd constructor thread ID: %d" % QtCore.QThread.currentThreadId())
        self.motor = MotorInit()

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.move_ra)
        self.moveRaCount = 0
        self.timer.start()

    def move_ra(self):
        j = 0
        print("MoveRA thread ID: %d" % QtCore.QThread.currentThreadId())
        if (not GPIO.input(_RA1_PIN)) and (not GPIO.input(_RA2_PIN)):  # If both pins are on
            j = 2  # Set the variable to the next state
            print("We are at first statement")
        elif (not GPIO.input(_RA1_PIN)) and GPIO.input(_RA2_PIN):  # If just one pin is on
            j = 1
            print("We are at second statement")
        elif GPIO.input(_RA1_PIN) and (not GPIO.input(_RA2_PIN)):
            j = 0
            print("We are at third statement")
        print(j)
        self.motor.setStep(_steps_half[j][0], _steps_half[j][1], True)
        j = j + 1
        j = 0 if j == 3 else j
        self.moveRaCount = j

    def move_dec(self):
        if (not GPIO.input(_DEC1_PIN)) and (not GPIO.input(_DEC2_PIN)):  # If both pins are on
            j = 2  # Set the variable to the next state
        elif not GPIO.input(_DEC1_PIN):  # If just one pin is on
            j = 1
        else:
            j = 0
        self.motor.setStep(_steps_half[j][0], _steps_half[j][1], False)


class SteppingBckwd(QtCore.QObject):
    def __init__(self, parent=None):
        super(SteppingBckwd, self).__init__(parent)
        self.motor = MotorInit()

    def move_ra(self):
        if (not GPIO.input(_RA1_PIN)) and (not GPIO.input(_RA2_PIN)):  # If both pins are on
            j = 0 # Set the variable to the next state
        elif not GPIO.input(_RA1_PIN):  # If just one pin is on
            j = 2
        else:
            j = 1
        self.motor.setStep(_steps_half[j][0], _steps_half[j][1], True)

    def move_dec(self):
        if (not GPIO.input(_DEC1_PIN)) and (not GPIO.input(_DEC2_PIN)):  # If both pins are on
            j = 0  # Set the variable to the next state
        elif not GPIO.input(_DEC1_PIN):  # If just one pin is on
            j = 2
        else:
            j = 1
        self.motor.setStep(_steps_half[j][0], _steps_half[j][1], False)