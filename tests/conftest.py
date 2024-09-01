import os

import pytest

from tests.utils import DataBase


@pytest.fixture(scope="session")
def use_test_db():
    # refer: Unfazed/docker-compose.yml

    host = os.getenv("MYSQL_HOST", "mysql")
    port = int(os.getenv("MYSQL_PORT", 3306))
    password = os.getenv("MYSQL_ROOT_PASSWORD", "app")
    db = DataBase(host, port, "root", password)

    # create test database
    db.create_db("test_app")

    yield

    # drop test database
    db.drop_db("test_app")
