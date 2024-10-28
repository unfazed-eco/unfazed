import os
import time
from logging import LogRecord
from logging.handlers import BaseRotatingHandler


class UnfazedRotatingFileHandler(BaseRotatingHandler):
    def __init__(
        self,
        filename: str,
        mode: str = "a",
        maxBytes: int = 0,
        encoding: str = None,
        delay: bool = False,
    ):
        self.raw_filename = filename
        self.validate_filename(filename)
        filename = self.create_process_safe_name(filename)
        super().__init__(filename, mode, encoding, delay)
        self.maxBytes = maxBytes

    def validate_filename(self, filename: str):
        if not filename:
            raise ValueError("filename cannot be empty")

        if not filename.endswith(".log"):
            raise ValueError("filename must end with .log")

    def create_process_safe_name(self, filename: str):
        # create a process safe name with pid
        name, suffix = filename.rsplit(".", 1)
        return f"{name}_pid{os.getpid()}_ts{int(time.time())}.{suffix}"

    def namer(self, filename: str) -> str:
        name, suffix = filename.rsplit(".", 1)
        return f"{name}_archived.{suffix}"

    def shouldRollover(self, record: LogRecord):
        """
        Determine if rollover should occur.

        Basically, see if the supplied record would cause the file to exceed
        the size limit we have.
        """
        if os.path.exists(self.baseFilename) and not os.path.isfile(self.baseFilename):
            return False
        if self.stream is None:  # delay was set...
            self.stream = self._open()  # pragma: no cover  # TODO: add test
        if self.maxBytes > 0:  # are we rolling over?
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  # due to non-posix-compliant Windows feature
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return True
        return False

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        archived_filename = self.rotation_filename(self.baseFilename)
        if os.path.exists(archived_filename):
            os.remove(archived_filename)

        os.rename(self.baseFilename, archived_filename)

        new_filename = self.create_process_safe_name(self.raw_filename)
        self.baseFilename = new_filename

        if not self.delay:
            self.stream = self._open()
