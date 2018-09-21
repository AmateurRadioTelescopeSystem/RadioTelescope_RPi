import sys
import logging
import traceback
import threading
import multiprocessing
import logging.handlers


# ============================================================================
# Define Log Handler
# Initial code: https://mattgathu.github.io/multiprocessing-logging-in-python/
# ============================================================================
class CustomLogHandler(logging.Handler):
    """multiprocessing log handler

    This handler makes it possible for several processes
    to log to the same file by using a queue.

    """
    def __init__(self, fname, whn, enc, utc):
        logging.Handler.__init__(self)

        self.queue = multiprocessing.Queue(-1)
        self.fname = fname
        self.when = whn
        self.encoding = enc
        self.utc = utc
        self._handler = None

        thrd = threading.Thread(target=self.receive)
        thrd.daemon = True
        thrd.start()

    def setFormatter(self, fmt):
        self.fmt = fmt  # Save the format to use it for the handler later

    def receive(self):
        self._handler = logging.handlers.TimedRotatingFileHandler\
            (self.fname, self.when, encoding=self.encoding, utc=self.utc)
        logging.Handler.setFormatter(self, self.fmt)
        self._handler.setFormatter(self.fmt)
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
        self.queue.put_nowait(s)

    def emit(self, record):
        try:
            self.send(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        if self._handler is not None:
            self._handler.close()
        logging.Handler.close(self)
