import os
from pathlib import Path
from unittest.mock import patch

from aerich import DowngradeError

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

_Settings = {
    "DEBUG": True,
    "PROJECT_NAME": "test_app_db",
    "ROOT_URLCONF": "tests.apps.orm.routes",
    # "INSTALLED_APPS": ["tests.apps.orm.common", "tests.apps.orm.serializer"],
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
    unfazed1 = Unfazed(
        settings=UnfazedSettings(
            **_Settings,
            INSTALLED_APPS=["tests.apps.orm.common"],
        )
    )
    await unfazed1.setup()

    cmd = init_db.Command(
        unfazed=unfazed1, name="orm_test_makemigrations", app_label="orm_test_cmd"
    )

    await cmd.handle(**{"safe": True, "location": migrations_path})

    # check there must be a file under root_path / models
    models_path = migrations_path / "models"
    assert models_path.exists()
    assert len(list(models_path.glob("*.py"))) == 1

    # add a new model
    # app1
    unfazed2 = Unfazed(
        settings=UnfazedSettings(
            **_Settings,
            INSTALLED_APPS=["tests.apps.orm.common", "tests.apps.orm.serializer"],
        )
    )
    await unfazed2.setup()
    # migrate cmd
    cmd = migrate.Command(
        unfazed=unfazed2, name="orm_test_makemigrations", app_label="orm_test_cmd"
    )

    await cmd.handle(**{"location": migrations_path, "name": "add_group"})

    assert len(list(models_path.glob("*.py"))) == 2

    # upgrade
    cmd = upgrade.Command(
        unfazed=unfazed2, name="orm_test_migrate", app_label="orm_test_cmd"
    )

    await cmd.handle(**{"location": migrations_path, "transaction": True})

    # history
    cmd = history.Command(
        unfazed=unfazed2, name="orm_test_migrate", app_label="orm_test_cmd"
    )

    await cmd.handle(**{"location": migrations_path})

    # heads
    cmd = heads.Command(
        unfazed=unfazed2, name="orm_test_migrate", app_label="orm_test_cmd"
    )

    await cmd.handle(**{"location": migrations_path})

    # downgrade
    cmd = downgrade.Command(
        unfazed=unfazed2, name="orm_test_migrate", app_label="orm_test_cmd"
    )
    await cmd.handle(**{"location": migrations_path, "version": 1, "delete": True})

    # inspectdb
    cmd = inspectdb.Command(
        unfazed=unfazed2, name="orm_test_migrate", app_label="orm_test_cmd"
    )
    await cmd.handle(**{"location": migrations_path})


async def test_full_coverage():
    unfazed1 = Unfazed(
        settings=UnfazedSettings(
            **_Settings,
            INSTALLED_APPS=["tests.apps.orm.common"],
        )
    )
    await unfazed1.setup()

    with patch("aerich.Command.init") as init_func:
        init_func.return_value = None

        with patch("aerich.Command.downgrade") as downgrade_func:
            downgrade_func.return_value = ["1"]
            downgrade_func.side_effect = DowngradeError("error")
            cmd = downgrade.Command(
                unfazed=unfazed1, name="orm_test_migrate", app_label="orm_test_cmd"
            )
            await cmd.handle(**{"location": "migrations", "version": 1, "delete": True})

        with patch("aerich.Command.heads") as heads_func:
            # heads
            heads_func.return_value = ["1", "2"]
            cmd = heads.Command(
                unfazed=unfazed1, name="orm_test_migrate", app_label="orm_test_cmd"
            )
            await cmd.handle(**{"location": "migrations"})

        with patch("aerich.Command.history") as history_func:
            # history
            history_func.return_value = []
            cmd = history.Command(
                unfazed=unfazed1, name="orm_test_migrate", app_label="orm_test_cmd"
            )
            await cmd.handle(**{"location": "migrations"})

        with patch("aerich.Command.init_db") as initdb_func:
            initdb_func.return_value = None
            initdb_func.side_effect = FileExistsError("error")
            cmd = init_db.Command(
                unfazed=unfazed1, name="orm_test_migrate", app_label="orm_test_cmd"
            )
            await cmd.handle(**{"location": "migrations", "safe": True})

        with patch("aerich.Command.migrate") as migrate_func:
            migrate_func.return_value = None
            cmd = migrate.Command(
                unfazed=unfazed1, name="orm_test_migrate", app_label="orm_test_cmd"
            )
            await cmd.handle(**{"location": "migrations", "name": "add_group"})

        with patch("aerich.Command.upgrade") as upgrade_func:
            upgrade_func.return_value = None
            cmd = upgrade.Command(
                unfazed=unfazed1, name="orm_test_migrate", app_label="orm_test_cmd"
            )
            await cmd.handle(**{"location": "migrations", "transaction": True})
