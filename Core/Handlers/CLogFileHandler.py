import os
import sys
import gzip
import logging
import traceback
import threading
import multiprocessing
import logging.handlers


# ============================================================================
# Define a Custom Log File Handler
# Initial code: https://mattgathu.github.io/multiprocessing-logging-in-python/
# Code for compression, retrieved from logging docs:
# https://docs.python.org/3/howto/logging-cookbook.html#using-a-rotator-and-namer-to-customize-log-rotation-processing
# ============================================================================
class CustomLogHandler(logging.Handler):
    """multiprocessing log handler

    This handler makes it possible for several processes
    to log to the same file by using a queue.

    """
    def __init__(self, filename, when, backup_count, enc, utc):
        """
        Class constructor to make the necessary initializations.

        :param filename: The name of the logging file
        :param when: When to rotate
        :param backup_count: Max number of old files to keep
        :param enc: Log file's encoding
        :param utc: UTC to be used as logging time
        :type filename str
        :type when str
        :type backup_count int
        :type enc str
        :type utc bool
        """
        logging.Handler.__init__(self)

        self.queue = multiprocessing.Queue(-1)
        self.fname = filename
        self.when = when
        self.encoding = enc
        self.utc = utc
        self.backup_count = backup_count
        self._handler = None

        thrd = threading.Thread(target=self.receive)
        thrd.daemon = True
        thrd.start()

    def setFormatter(self, fmt):
        """
        Set the formatter for the file handler

        :param fmt: Formatter string as passed from the configuration
        :type fmt str
        :return: Nothing
        """
        self.fmt = fmt  # Save the format to use it for the handler later

    def receive(self):
        """
        Receive the logging message an perform logging.

        :return: Nothing
        """
        self._handler = logging.handlers.TimedRotatingFileHandler\
            (self.fname, self.when, backupCount=self.backup_count, encoding=self.encoding, utc=self.utc)
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
                    dummy = self.format(record)
                    record.exc_info = None
                self._handler.emit(record)  # Write to log file
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except:
                traceback.print_exc(file=sys.stderr)

    def send(self, s):
        """
        Send the log message to the logging queue, in order to be logged.

        :param s: Message object
        :type s object
        :return: Nothing
        """
        self.queue.put_nowait(s)

    def emit(self, record):
        """
        Emit the log recording signal by sending the message to the queue

        :param record: Message record
        :return: Nothing
        """
        try:
            self.send(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        """
        Close the handler upon request.

        :return: Nothing
        """
        if self._handler is not None:
            self._handler.close()
        logging.Handler.close(self)

    def compressor(self, source, dest):
        """
        Compress the file on every rotation

        :param source: Source file name
        :param dest: Destination file name
        :type source str
        :type dest str
        :return: Nothing
        """
        with open(source, "rb") as source_file:
            data = source_file.read()  # Read the data from file and compress them
            compressed = gzip.compress(data, 9)  # Get the compressed binary data
            with open(dest, "wb") as dest_file:
                dest_file.write(compressed)  # Save the compressed data to file
        os.remove(source) # Remove uncompressed file

    def namer(self, name):
        """
        Append the appropriate suffix to the compressed file name

        :param name: File name to append suffix
        :type name str
        :return: Nothing
        """
        return name + ".gz"
