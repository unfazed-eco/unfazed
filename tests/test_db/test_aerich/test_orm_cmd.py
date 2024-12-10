import os
import typing as t
from pathlib import Path
from unittest.mock import patch

import pytest
from aerich import DowngradeError
from tortoise import Tortoise

from unfazed.conf import UnfazedSettings
from unfazed.core import Unfazed
from unfazed.db.tortoise.commands import (
    downgrade,
    heads,
    history,
    init_db,
    inspectdb,
    migrate,
    upgrade,
)


@pytest.fixture(autouse=True)
def setup_aerich_env() -> t.Generator:
    Tortoise.apps = {}
    Tortoise._inited = False

    yield


_Settings = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_db",
    "ROOT_URLCONF": "tests.apps.orm.routes",
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


async def test_cmd(tmp_path: Path) -> None:
    # create a tmp path
    root_path = tmp_path / "orm"
    root_path.mkdir()

    migrations_path = root_path / "migrations"

    # app1

    APP1_SETTINGS = {
        **_Settings,
        "INSTALLED_APPS": ["tests.apps.orm.common"],
    }
    unfazed1 = Unfazed(settings=UnfazedSettings.model_validate(APP1_SETTINGS))
    await unfazed1.setup()

    init_db_cmd = init_db.Command(
        unfazed=unfazed1, name="orm_test_makemigrations", app_label="orm_test_cmd"
    )

    await init_db_cmd.handle(**{"safe": True, "location": migrations_path})

    # check there must be a file under root_path / models
    models_path = migrations_path / "models"
    assert models_path.exists()
    assert len(list(models_path.glob("*.py"))) == 1

    # add a new model
    # app1
    APP2_SETTINGS = {
        **_Settings,
        "INSTALLED_APPS": ["tests.apps.orm.common", "tests.apps.orm.other"],
    }
    unfazed2 = Unfazed(settings=UnfazedSettings.model_validate(APP2_SETTINGS))
    await unfazed2.setup()
    # migrate cmd
    migrate_cmd = migrate.Command(
        unfazed=unfazed2, name="orm_test_makemigrations", app_label="orm_test_cmd"
    )

    await migrate_cmd.handle(**{"location": migrations_path, "name": "add_group"})

    assert len(list(models_path.glob("*.py"))) == 2

    # upgrade
    upgrade_cmd = upgrade.Command(
        unfazed=unfazed2, name="orm_test_migrate", app_label="orm_test_cmd"
    )

    await upgrade_cmd.handle(**{"location": migrations_path, "transaction": True})

    # history
    history_cmd = history.Command(
        unfazed=unfazed2, name="orm_test_migrate", app_label="orm_test_cmd"
    )

    await history_cmd.handle(**{"location": migrations_path})

    # heads
    heads_cmd = heads.Command(
        unfazed=unfazed2, name="orm_test_migrate", app_label="orm_test_cmd"
    )

    await heads_cmd.handle(**{"location": migrations_path})

    # downgrade
    downgrade_cmd = downgrade.Command(
        unfazed=unfazed2, name="orm_test_migrate", app_label="orm_test_cmd"
    )
    await downgrade_cmd.handle(
        **{"location": migrations_path, "version": 1, "delete": True}
    )

    # inspectdb
    inspectdb_cmd = inspectdb.Command(
        unfazed=unfazed2, name="orm_test_migrate", app_label="orm_test_cmd"
    )
    await inspectdb_cmd.handle(**{"location": migrations_path})


async def test_full_coverage() -> None:
    SETTINGS = {
        **_Settings,
        "INSTALLED_APPS": ["tests.apps.orm.common"],
    }
    unfazed1 = Unfazed(settings=UnfazedSettings.model_validate(SETTINGS))
    await unfazed1.setup()

    with patch("aerich.Command.init") as init_func:
        init_func.return_value = None

        with patch("aerich.Command.downgrade") as downgrade_func:
            downgrade_func.return_value = ["1"]
            downgrade_func.side_effect = DowngradeError("error")
            downgrade_cmd = downgrade.Command(
                unfazed=unfazed1, name="orm_test_migrate", app_label="orm_test_cmd"
            )
            await downgrade_cmd.handle(
                **{"location": "migrations", "version": 1, "delete": True}
            )

        with patch("aerich.Command.heads") as heads_func:
            # heads
            heads_func.return_value = ["1", "2"]
            heads_cmd = heads.Command(
                unfazed=unfazed1, name="orm_test_migrate", app_label="orm_test_cmd"
            )
            await heads_cmd.handle(**{"location": "migrations"})

        with patch("aerich.Command.history") as history_func:
            # history
            history_func.return_value = []
            history_cmd = history.Command(
                unfazed=unfazed1, name="orm_test_migrate", app_label="orm_test_cmd"
            )
            await history_cmd.handle(**{"location": "migrations"})

        with patch("aerich.Command.init_db") as initdb_func:
            initdb_func.return_value = None
            initdb_func.side_effect = FileExistsError("error")
            init_db_cmd = init_db.Command(
                unfazed=unfazed1, name="orm_test_migrate", app_label="orm_test_cmd"
            )
            await init_db_cmd.handle(**{"location": "migrations", "safe": True})

        with patch("aerich.Command.migrate") as migrate_func:
            migrate_func.return_value = None
            migrate_cmd = migrate.Command(
                unfazed=unfazed1, name="orm_test_migrate", app_label="orm_test_cmd"
            )
            await migrate_cmd.handle(**{"location": "migrations", "name": "add_group"})

        with patch("aerich.Command.upgrade") as upgrade_func:
            upgrade_func.return_value = None
            upgrade_cmd = upgrade.Command(
                unfazed=unfazed1, name="orm_test_migrate", app_label="orm_test_cmd"
            )
            await upgrade_cmd.handle(**{"location": "migrations", "transaction": True})
