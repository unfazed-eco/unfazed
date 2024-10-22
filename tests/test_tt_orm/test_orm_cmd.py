import os
from pathlib import Path

from unfazed.const import UNFAZED_SETTINGS_MODULE
from unfazed.core import Unfazed
from unfazed.db.tortoise.commands import (
    downgrade,
    heads,
    history,
    init_db,
    migrate,
    upgrade,
)


async def test_cmd(tmp_path: Path) -> None:
    os.environ[UNFAZED_SETTINGS_MODULE] = "tests.apps.orm.settings"
    unfazed = Unfazed()
    await unfazed.setup()
    root_path = tmp_path / "orm"
    root_path.mkdir()

    migrations_path = root_path / "migrations"

    cmd = init_db.Command(
        unfazed=unfazed, name="orm_test_makemigrations", app_label="orm_test_cmd"
    )

    await cmd.handle(**{"safe": True, "location": migrations_path})

    # check there must be a file under root_path / models
    models_path = migrations_path / "models"
    assert models_path.exists()
    assert len(list(models_path.glob("*.py"))) == 1

    # add a new model
    # migrate cmd
    cmd = migrate.Command(
        unfazed=unfazed, name="orm_test_makemigrations", app_label="orm_test_cmd"
    )

    await cmd.handle(**{"location": migrations_path, "name": "add_group"})

    # upgrade
    # only check if the cmd runs without error
    cmd = upgrade.Command(
        unfazed=unfazed, name="orm_test_migrate", app_label="orm_test_cmd"
    )

    await cmd.handle(**{"location": migrations_path, "transaction": True})

    # history
    cmd = history.Command(
        unfazed=unfazed, name="orm_test_migrate", app_label="orm_test_cmd"
    )

    await cmd.handle(**{"location": migrations_path})

    # heads
    cmd = heads.Command(
        unfazed=unfazed, name="orm_test_migrate", app_label="orm_test_cmd"
    )

    await cmd.handle(**{"location": migrations_path})

    # downgrade
    cmd = downgrade.Command(
        unfazed=unfazed, name="orm_test_migrate", app_label="orm_test_cmd"
    )
    await cmd.handle(**{"location": migrations_path, "version": 1, "delete": True})
