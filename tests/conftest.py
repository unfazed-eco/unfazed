import os
import typing as t
from pathlib import Path

import pytest
import pytest_asyncio
from pytest import Item
from pytest_asyncio import is_async_test

from tests.utils import DataBase
from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed
from unfazed.db.tortoise.commands import init_db, migrate


# dont need decorate test functions with pytest.mark.asyncio
def pytest_collection_modifyitems(items: t.List[Item]) -> None:
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        # skip if already marked
        if list(async_test.iter_markers()):
            continue
        async_test.add_marker(session_scope_marker, append=False)


@pytest.fixture(scope="session")
def use_test_db() -> t.Any:
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


_Settings = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_db",
    "ROOT_URLCONF": "tests.apps.routes",
    "INSTALLED_APPS": [
        "tests.apps.orm.common",
        "tests.apps.orm.serializer",
        "tests.apps.admin.account",
        "tests.apps.admin.article",
        "unfazed.contrib.admin",
    ],
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "unfazed.db.tortoise.backends.mysql",
                "CREDENTIALS": {
                    "HOST": os.environ.get("MYSQL_HOST", "mysql"),
                    "PORT": int(os.environ.get("MYSQL_PORT", 3306)),
                    "USER": "root",
                    "PASSWORD": "app",
                    "DATABASE": "test_app",
                },
            }
        }
    },
}


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_unfazed(tmp_path_factory: Path, use_test_db: t.Generator) -> t.Any:
    # init unfazed
    unfazed = Unfazed(settings=UnfazedSettings(**_Settings))

    await unfazed.setup()

    import asyncio

    loop = asyncio.get_running_loop()
    print(f"prepare_unfazed {loop} - {id(loop)}")

    root_path = tmp_path_factory.mktemp("unfazed")
    # create migrations

    migrations_path = root_path / "migrations"

    cmd = init_db.Command(
        unfazed=unfazed, name="unfazed_test", app_label="unfazed_test"
    )

    await cmd.handle(**{"safe": True, "location": migrations_path})

    # migrate cmd
    cmd = migrate.Command(
        unfazed=unfazed, name="unfazed_test", app_label="unfazed_test"
    )

    await cmd.handle(**{"location": migrations_path, "name": "add car model"})

    yield unfazed
