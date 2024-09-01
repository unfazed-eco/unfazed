import pytest

from tests.utils import DataBase


@pytest.fixture(scope="session")
def use_test_db():
    # refer: Unfazed/docker-compose.yml
    db = DataBase("127.0.0.1", 3306, "root", "app")

    # create test database
    db.create_db("test_app")

    yield

    # drop test database
    db.drop_db("test_app")
