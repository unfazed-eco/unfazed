import os
import socket
import time
import typing as t
from logging import LogRecord
from logging.handlers import BaseRotatingHandler


class UnfazedRotatingFileHandler(BaseRotatingHandler):
    """
    A process-safe rotating file handler for logging.

    This handler creates unique log files for each process by appending the process ID
    and timestamp to the filename. It supports log rotation based on file size.

    Features:
        - Process-safe logging with unique filenames
        - Automatic log rotation based on file size
        - Support for delayed file opening
        - Customizable encoding

    Args:
        filename (str): The base filename for the log file. Must end with '.log'.
        mode (str, optional): The file opening mode. Defaults to 'a'.
        maxBytes (int, optional): Maximum size in bytes before rotation. Defaults to 0 (no rotation).
        encoding (str | None, optional): File encoding. Defaults to None.
        delay (bool, optional): If True, delay file opening until first write. Defaults to False.

    Raises:
        ValueError: If filename is empty or doesn't end with '.log'.
        OSError: If there are issues with file operations.

    Example:
        >>> handler = UnfazedRotatingFileHandler(
        ...     filename="app.log",
        ...     maxBytes=1024*1024,  # 1MB
        ...     encoding="utf-8"
        ... )
    """

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        maxBytes: int = 0,
        encoding: str | None = None,
        delay: bool = False,
    ) -> None:
        self.raw_filename = filename
        self.validate_filename(filename)
        filename = self.create_process_safe_name(filename)
        super().__init__(filename, mode, encoding, delay)
        self.maxBytes = maxBytes

    def validate_filename(self, filename: str) -> None:
        """
        Validate the log filename.

        Args:
            filename (str): The filename to validate.

        Raises:
            ValueError: If filename is empty or doesn't end with '.log'.
        """
        if not filename:
            raise ValueError("filename cannot be empty")

        if not filename.endswith(".log"):
            raise ValueError("filename must end with .log")

    def create_process_safe_name(self, filename: str) -> str:
        """
        Create a process-safe filename by appending hostname, PID and timestamp.

        Args:
            filename (str): The base filename.

        Returns:
            str: A process-safe filename with format: {name}_{hostname}_pid{pid}_ts{timestamp}.log
        """
        name, suffix = filename.rsplit(".", 1)
        return f"{name}_{socket.gethostname()}_pid{os.getpid()}_ts{int(time.time())}.{suffix}"

    @t.override
    def namer(self, filename: str) -> str:  # type: ignore
        name, suffix = filename.rsplit(".", 1)
        return f"{name}_archived.{suffix}"

    def shouldRollover(self, record: LogRecord) -> bool:
        """
        Determine if log rotation should occur based on file size.

        Args:
            record (LogRecord): The log record to be written.

        Returns:
            bool: True if rotation should occur, False otherwise.
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

    def doRollover(self) -> None:
        """
        Perform the log rotation.

        This method:
        1. Closes the current log file
        2. Renames the current file to an archived name
        3. Creates a new log file with a process-safe name
        4. Opens the new file if not in delay mode

        Raises:
            OSError: If there are issues with file operations.
        """
        if self.stream:
            self.stream.close()
            self.stream = None  # type: ignore

        archived_filename = self.rotation_filename(self.baseFilename)
        if os.path.exists(archived_filename):
            os.remove(archived_filename)

        os.rename(self.baseFilename, archived_filename)

        new_filename = self.create_process_safe_name(self.raw_filename)
        self.baseFilename = new_filename

        if not self.delay:
            self.stream = self._open()
