from pathlib import Path

import pytest

from unfazed.command.internal.startapp import Command as StartAppCommand
from unfazed.command.internal.startproject import Command as StartProjectCommand
from unfazed.core import Unfazed


async def test_start_cmd(tmp_path: Path) -> None:
    unfazed = Unfazed()
    project_path = tmp_path / "start_cmd"

    project_path.mkdir()

    start_project = StartProjectCommand(
        unfazed=unfazed, name="start_project_cmd", app_label="start_cmd"
    )
    await start_project.handle(project_name="myproject", location=str(project_path))

    assert (project_path / "myproject").exists()
    assert (project_path / "myproject" / "deploy").exists()
    assert (project_path / "myproject" / "docs").exists()
    assert (project_path / "myproject" / "src").exists()
    assert (project_path / "myproject" / ".gitignore").exists()
    assert (project_path / "myproject" / "README.md").exists()
    assert (project_path / "myproject" / "changelog.md").exists()
    assert (project_path / "myproject" / "src" / "backend").exists()
    assert (project_path / "myproject" / "src" / "docker-compose.yml").exists()
    assert (project_path / "myproject" / "src" / "Dockerfile").exists()
    assert (project_path / "myproject" / "src" / "backend" / "entry").exists()
    assert (project_path / "myproject" / "src" / "backend" / "Makefile").exists()
    assert (project_path / "myproject" / "src" / "backend" / "manage.py").exists()
    assert (project_path / "myproject" / "src" / "backend" / "pyproject.toml").exists()
    assert (
        project_path / "myproject" / "src" / "backend" / "entry" / "settings"
    ).exists()
    assert (
        project_path
        / "myproject"
        / "src"
        / "backend"
        / "entry"
        / "settings"
        / "__init__.py"
    ).exists()
    assert (
        project_path / "myproject" / "src" / "backend" / "entry" / "__init__.py"
    ).exists()
    assert (
        project_path / "myproject" / "src" / "backend" / "entry" / "routes.py"
    ).exists()
    assert (
        project_path / "myproject" / "src" / "backend" / "entry" / "asgi.py"
    ).exists()

    be_path = project_path / "myproject" / "src" / "backend"

    start_app = StartAppCommand(
        unfazed=unfazed, name="start_app_cmd", app_label="start_cmd"
    )
    await start_app.handle(
        app_name="simpleapp", location=str(be_path), template="simple"
    )

    assert (be_path / "simpleapp").exists()
    assert (be_path / "simpleapp" / "models.py").exists()
    assert (be_path / "simpleapp" / "endpoints.py").exists()
    assert (be_path / "simpleapp" / "routes.py").exists()
    assert (be_path / "simpleapp" / "serializers.py").exists()
    assert (be_path / "simpleapp" / "services.py").exists()
    assert (be_path / "simpleapp" / "schema.py").exists()
    assert (be_path / "simpleapp" / "admin.py").exists()
    assert (be_path / "simpleapp" / "app.py").exists()
    assert (be_path / "simpleapp" / "settings.py").exists()
    assert (be_path / "simpleapp" / "tests.py").exists()

    start_app = StartAppCommand(
        unfazed=unfazed, name="start_complex_app_cmd", app_label="start_cmd"
    )

    await start_app.handle(
        app_name="complexapp", location=str(be_path), template="standard"
    )

    assert (be_path / "complexapp").exists()
    assert (be_path / "complexapp" / "models" / "__init__.py").exists()
    assert (be_path / "complexapp" / "schema" / "request" / "__init__.py").exists()
    assert (be_path / "complexapp" / "schema" / "response" / "__init__.py").exists()
    assert (be_path / "complexapp" / "serializers" / "__init__.py").exists()
    assert (be_path / "complexapp" / "services" / "__init__.py").exists()
    assert (be_path / "complexapp" / "endpoints" / "__init__.py").exists()
    assert (be_path / "complexapp" / "admin.py").exists()
    assert (be_path / "complexapp" / "app.py").exists()
    assert (be_path / "complexapp" / "settings.py").exists()
    assert (be_path / "complexapp" / "tests" / "test_all.py").exists()


async def test_failed_startapp(tmp_path: Path) -> None:
    unfazed = Unfazed()

    project_path = tmp_path / "failed_startapp"
    project_path.mkdir()

    cmd = StartAppCommand(unfazed=unfazed, name="failed_startapp", app_label="failed")

    with pytest.raises(ValueError):
        await cmd.handle(
            app_name="simpleapp", location=str(project_path), template="wrongtemplate"
        )

    existed_app = project_path / "existedapp"

    existed_app.mkdir()

    with pytest.raises(FileExistsError):
        await cmd.handle(
            app_name="existedapp", location=str(project_path), template="simple"
        )


async def test_failed_startprj(tmp_path: Path) -> None:
    unfazed = Unfazed()

    project_path = tmp_path / "failed_startprj"
    project_path.mkdir()

    cmd = StartProjectCommand(
        unfazed=unfazed, name="failed_startprj", app_label="failed"
    )

    with pytest.raises(FileExistsError):
        await cmd.handle(project_name="failed_startprj", location=str(tmp_path))
