import os
import typing as t
from pathlib import Path

import pytest
from unfazed.command import BaseCommand
from unfazed.command.internal.startapp import Command as StartAppCommand
from unfazed.command.internal.startproject import Command as StartProjectCommand
from unfazed.core import Unfazed


@pytest.mark.asyncio
async def test_project_app_create(tmp_path: Path):
    unfazed = Unfazed()

    # create a new project
    cmd = StartProjectCommand(
        unfazed=unfazed, name="startproject", app_label="startproject"
    )

    await cmd.handle(name="backend", directory=tmp_path, template=cmd.template)

    # check project structure
    assert (tmp_path / "backend").exists()
    assert (tmp_path / "backend" / "backend").exists()
    assert (tmp_path / "backend" / "backend" / "__init__.py").exists()
    assert (tmp_path / "backend" / "backend" / "settings.py").exists()
    assert (tmp_path / "backend" / "backend" / "urls.py").exists()
    assert (tmp_path / "backend" / "backend" / "asgi.py").exists()
    assert (tmp_path / "backend" / "manage.py").exists()

    # create a new app
    cmd = StartAppCommand(unfazed=unfazed, name="startapp", app_label="startapp")
    await cmd.handle(name="app", directory=tmp_path / "backend", template=cmd.template)

    # check app structure
    assert (tmp_path / "backend" / "app").exists()
    assert (tmp_path / "backend" / "app" / "__init__.py").exists()
    assert (tmp_path / "backend" / "app" / "views.py").exists()
    assert (tmp_path / "backend" / "app" / "models.py").exists()
    assert (tmp_path / "backend" / "app" / "urls.py").exists()
    assert (tmp_path / "backend" / "app" / "admin.py").exists()
    assert (tmp_path / "backend" / "app" / "app.py").exists()
    assert (tmp_path / "backend" / "app" / "tests").exists()
    assert (tmp_path / "backend" / "app" / "tests" / "test_all.py").exists()


def test_command_center():
    os.environ["UNFAZED_SETTINGS_MODULE"] = "unfazedproject.settings"
    unfazed = Unfazed()

    unfazed.setup_commands()

    command_map: t.Mapping[str, BaseCommand] = unfazed.command_center.commands

    assert "cmd1" in command_map
    assert "runserver" in command_map
    assert "startapp" in command_map
    assert "startproject" in command_map
