import os
from pathlib import Path

import pytest

from unfazed.command.internal import init_db
from unfazed.const import UNFAZED_SETTINGS_MODULE
from unfazed.core import Unfazed


@pytest.mark.asyncio(loop_scope="module")
async def test_cmd(tmp_path: Path):
    # set_event_loop(event_loop)
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
