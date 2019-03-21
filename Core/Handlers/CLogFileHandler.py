import os
import sys
import gzip
import logging
import logging.handlers
import traceback
import threading
import multiprocessing


# ============================================================================
# Define a Custom Log File Handler
# Initial code: https://mattgathu.github.io/multiprocessing-logging-in-python/
# Code for compression, retrieved from logging docs:
# https://docs.python.org/3/howto/logging-cookbook.html#using-a-rotator-and-namer-to-customize-log-rotation-processing
# ============================================================================
class CustomLogHandler(logging.Handler):
    """Multiprocessing logging handler

    This handler makes it possible for several processes
    to log to the same file by using a queue.

    """

    def __init__(self, filename, when, backup_count, enc, utc):
        """Class constructor to make the necessary initializations

        Args:
            filename (str): The name of the logging file
            when (str): When to rotate
            backup_count (int): Max number of old files to keep
            enc (str): Log file's encoding
            utc (bool): UTC to be used as logging time
        """
        logging.Handler.__init__(self)

        self.queue = multiprocessing.Queue(-1)
        self.fname = filename
        self.when = when
        self.encoding = enc
        self.utc = utc
        self.backup_count = backup_count
        self._handler = None
        self.fmt = None  # Declare the variable for the formatter

        # Enable threaded logging
        thrd = threading.Thread(target=self.receive)  # Create the logging thread
        thrd.daemon = True  # Enable the threading daemon
        thrd.start()  # Start the logging thread

    def setFormatter(self, fmt):
        """Set the formatter for the file handler

        A reimplementation, `override`, of the :meth:`logging.Handler.setFormatter` function from the :mod:`logging`
        module. It just sets the class's global formatter variable equal to the provided formatter string.

        Todo:
            Resolve the general exception issue. Add the expected exception type.

        Args:
            fmt (str): Formatter string as received from the configuration

        Returns:
            Nothing
        """
        self.fmt = fmt  # Save the format to use it for the handler later

    def receive(self):
        """Receive the logging message and write it to the log file.

        Receives the message signal issued by the logger object and performs the necessary steps to write the log to
        the specified file.

        Todo:
            Check whether the ``dummy`` variable is required. Also define if a ``None`` type check is required for
            the formatter string.

        Returns:
            Nothing
        """
        self._handler = logging.handlers.TimedRotatingFileHandler(self.fname, self.when, backupCount=self.backup_count,
                                                                  encoding=self.encoding, utc=self.utc)
        logging.Handler.setFormatter(self, self.fmt)
        self._handler.setFormatter(self.fmt)
        self._handler.rotator = self.compressor  # Compress the old file in every rotation
        self._handler.namer = self.namer  # Name the compressed file
        while True:
            try:
                record = self.queue.get()  # Get the data from the queue
                if record.args:
                    record.msg = record.msg % record.args
                    record.args = None
                if record.exc_info:
                    # dummy = self.format(record) todo: Define if this has existential meaning
                    record.exc_info = None
                self._handler.emit(record)  # Write to log file
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:  # noqa
                traceback.print_exc(file=sys.stderr)

    def send(self, s):
        """Send the log message to the logging queue, in order to be appended to the logging file.

        Append the message to the queue. Send the message to the queue with no delay.

        Args:
            s (object): Message object

        Returns:
            Nothing
        """
        self.queue.put_nowait(s)

    def emit(self, record):
        """Emit the log recording signal by sending the message to the queue

        Sends the received message to the logging queue to be logged.

        Todo:
            Resolve the general exception issue. Add the expected exception type.

        Args:
            record: Logging message to record

        Returns:
            Nothing
        """
        try:
            self.send(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:  # noqa
            self.handleError(record)

    def close(self):
        """Close the handler upon request.

        The :class:`logging.Handler` object is released and the logging file is closed.

        Returns:
            Nothing
        """
        if self._handler is not None:
            self._handler.close()
        logging.Handler.close(self)

    def compressor(self, source, dest):
        """Compress the provided file

        Performs a ``gzip`` compression of the provided source file. The compressed file is saved at the provided
        destination path.

        Todo:
            Decide whether this method will be transferred to a file on its own along with the :meth:`namer` below,
            to provide file compression utilities.

        Args:
            source (str): Path of the source file
            dest (str): Path to save the compressed file

        Returns:
            Nothing
        """
        with open(source, "rb") as source_file:
            data = source_file.read()  # Read the data from file and compress them
            compressed = gzip.compress(data, 9)  # Get the compressed binary data
            with open(dest, "wb") as dest_file:
                dest_file.write(compressed)  # Save the compressed data to file
        os.remove(source)  # Remove uncompressed file

    def namer(self, name):
        """Appends the appropriate suffix to the compressed file name

        This is used by the :class:`logging.handlers.TimedRotatingFileHandler` to append the correct suffix to the
        compressed backup file. The file name is provided as an argument an it is automatically assigned by the
        aforementioned class.

        Todo:
            Define whether this function should be moved to a separate file, the same thing as the :meth:`compressor`
            method

        Args:
            name (str): The file name to append the suffix at

        Returns:
            Nothing
        """
        return name + ".gz"
