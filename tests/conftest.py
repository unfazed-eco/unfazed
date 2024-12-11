import os
import typing as t

import pytest
from pytest import Item
from pytest_asyncio import is_async_test

from tests.utils import DataBase


# dont need decorate test functions with pytest.mark.asyncio
def pytest_collection_modifyitems(items: t.List[Item]) -> None:
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture(scope="session", autouse=True)
def use_test_db() -> t.Generator:
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
