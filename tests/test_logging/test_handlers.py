import os
from logging import getLogger
from pathlib import Path

import pytest

from unfazed.logging.handlers import UnfazedRotatingFileHandler


def test_rotating_file_handler(tmp_path: Path):
    path = tmp_path / "test.log"
    filename = str(path)

    text = "foobarfoobar"
    max_bytes = len(text) - 1
    handler = UnfazedRotatingFileHandler(filename=filename, maxBytes=max_bytes)

    logger = getLogger("test")

    logger.addHandler(handler)

    logger.info(text)
    logger.info(text)
    logger.info(text)

    # check if there's two files
    assert len(list(tmp_path.iterdir())) == 2

    # failed cases
    with pytest.raises(ValueError):
        UnfazedRotatingFileHandler(filename="")

    with pytest.raises(ValueError):
        wrong_path = tmp_path / "test"
        UnfazedRotatingFileHandler(filename=str(wrong_path))

    path = tmp_path / "test2.log"
    handler = UnfazedRotatingFileHandler(filename=str(path), maxBytes=10)
    filename = handler.create_process_safe_name(str(path))

    # delete the file
    if os.path.exists(filename):
        os.remove(filename)
    os.mkdir(filename)

    assert handler.shouldRollover("foobar") is False

    # maxBytes is 0
    path = tmp_path / "test3.log"
    handler = UnfazedRotatingFileHandler(filename=str(path), maxBytes=0)
    assert handler.shouldRollover("foobar") is False
