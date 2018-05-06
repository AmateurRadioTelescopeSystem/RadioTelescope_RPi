import RPi.GPIO as GPIO
import threading
import time

_steps_half = [[1, 0], [1, 1], [0, 1], []]
_steps_full = [[1, 0], [0, 1]]

# Set the pin numbers where the output is going to be
_RA1_PIN = 7
_RA2_PIN = 8
_DEC1_PIN = 10
_DEC2_PIN = 12

# TODO make the class a a QObject, so we can use QThreads to take advantage of signals and slots


class motor(object):
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

    def stepping_fwd(self, delay, steps, RA_motor, stp_full=False):
        j = 0  # Initialize the indexing variable
        step = 0
        thr = threading.currentThread()

        # Set the indexing variable, according to the current pin setting
        if RA_motor:
            if ((not GPIO.input(_RA1_PIN)) and (not GPIO.input(_RA2_PIN))):  # If both pins are on
                j = 2  # Set the variable to the next state
            elif (not GPIO.input(_RA1_PIN)):  # If just one pin is on
                j = 1
        else:
            if ((not GPIO.input(_DEC1_PIN)) and (not GPIO.input(_DEC2_PIN))):  # If both pins are on
                j = 2  # Set the variable to the next state
            elif (not GPIO.input(_DEC1_PIN)):  # If just one pin is on
                j = 1

        if stp_full:  # If full stepping is selected then do the following
            while getattr(thr, "run", True) and (step <= steps):
                self.setStep(_steps_full[j][0], _steps_full[j][1], RA_motor)
                time.sleep(delay)
                j = j + 1
                step = step + 1
                j = 0 if j == 2 else j
        else:
            while getattr(thr, "run", True) and (step <= steps):
                self.setStep(_steps_half[j][0], _steps_half[j][1], RA_motor)
                time.sleep(delay)
                j = j + 1
                step = step + 1
                j = 0 if j == 3 else j
        thr.done = True  # Indicate when we are done
        return True

    def stepping_bckwd(self, delay, steps, RA_motor, stp_full=False):
        j = 0  # Initialize the indexing variable
        step = 0
        thr = threading.currentThread()

        # Set the indexing variable, according to the current pin setting
        if RA_motor:
            if ((not GPIO.input(_RA1_PIN)) and (not GPIO.input(_RA2_PIN))):  # If both pins are on
                j = 2  # Set the variable to the next state
            elif (not GPIO.input(_RA1_PIN)):  # If just one pin is on
                j = 1
        else:
            if ((not GPIO.input(_DEC1_PIN)) and (not GPIO.input(_DEC2_PIN))):  # If both pins are on
                j = 2  # Set the variable to the next state
            elif (not GPIO.input(_DEC1_PIN)):  # If just one pin is on
                j = 1

        if stp_full:
            while getattr(thr, "run", True) and (step <= steps):
                self.setStep(_steps_full[1 - j][0], _steps_full[1 - j][1], RA_motor)
                time.sleep(delay)
                j = j + 1
                step = step + 1
                j = 0 if j == 2 else j
        else:
            while getattr(thr, "run", True) and (step <= steps):
                self.setStep(_steps_half[2 - j][0], _steps_half[2 - j][1], RA_motor)
                time.sleep(delay)
                j = j + 1
                step = step + 1
                j = 0 if j == 3 else j
        thr.done = True  # Indicate when we are done
        return True
