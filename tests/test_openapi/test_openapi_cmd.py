from pathlib import Path

from unfazed.command.internal.export_openapi import Command
from unfazed.core import Unfazed


async def test_export_openapi_cmd(
    setup_openapi_unfazed: Unfazed, tmp_path: Path
) -> None:
    tmp_dir = tmp_path / "test_export_openapi_cmd"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    unfazed = setup_openapi_unfazed

    cmd = Command(unfazed, "export_openapi", "internal")
    cmd.handle(location=tmp_dir)

    assert Path(tmp_dir / "openapi.yaml").exists()
