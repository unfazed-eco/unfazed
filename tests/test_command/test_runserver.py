from unittest import mock

import pytest

from unfazed.command.internal import runserver
from unfazed.core import Unfazed


async def test_runserver() -> None:
    unfazed = Unfazed()

    with pytest.raises(SystemExit):
        with mock.patch("uvicorn.server.Server.serve") as serve:
            serve.return_value = None

            commond = runserver.Command(
                unfazed=unfazed, name="runserver", app_label="runserver"
            )
            await commond.handle(
                host="127.0.0.1",
                port=8000,
                reload=False,
                workers=1,
                log_level="info",
            )

            serve.assert_called_once()

    with mock.patch("uvicorn.supervisors.ChangeReload") as cr:
        cr.run.return_value = None

        commond = runserver.Command(
            unfazed="unfazed", name="runserver", app_label="runserver"
        )
        await commond.handle(
            host="127.0.0.1",
            port=8000,
            reload=True,
            workers=1,
            log_level="info",
        )

        cr.assert_called_once()

    with mock.patch("uvicorn.supervisors.Multiprocess") as mp:
        mp.run.return_value = None

        commond = runserver.Command(
            unfazed=unfazed, name="runserver", app_label="runserver"
        )
        await commond.handle(
            host="127.0.0.1",
            port=8000,
            reload=False,
            workers=2,
            log_level="info",
        )

        mp.assert_called_once()
