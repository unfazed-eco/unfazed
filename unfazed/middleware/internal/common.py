import logging
import typing as t
from traceback import format_exc, format_exception

import orjson as json
from jinja2 import Template

from unfazed.conf import UnfazedSettings, settings
from unfazed.core import Unfazed
from unfazed.http import HtmlResponse, HttpResponse
from unfazed.middleware import BaseMiddleware
from unfazed.type import ASGIApp, Receive, Scope, Send

logger = logging.getLogger("unfazed.middleware")

TEMPLATE = """

<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UNFAZED DEBUG PAGE</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            color: #333;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #e74c3c;
        }
        pre {
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <h1>Unfazed Error Info</h1>
    <p> you can see this page because DEBUG = True in the settings file. </p>
    <div class="container">
        <h2>TRACEBACK</h2>
        <pre>{{ error_message }}</pre>
    </div>
    <br>
    <div class="container">
        <h2>SETTINGS</h2>
        <pre>{{ unfazed_settings }}</pre>
    </div>
</body>
</html>


"""


def render_error_html(error: Exception, unfazed_settings: t.Dict[str, t.Any]) -> str:
    error_content_list = format_exception(type(error), error, error.__traceback__)
    error_content = "".join(error_content_list)
    unfazed_settings_str = json.dumps(
        unfazed_settings, option=json.OPT_INDENT_2
    ).decode()

    content = Template(TEMPLATE).render(
        {"error_message": error_content, "unfazed_settings": unfazed_settings_str}
    )

    return content


class CommonMiddleware(BaseMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        unfazed_settings: UnfazedSettings = settings["UNFAZED_SETTINGS"]
        self.debug = unfazed_settings.DEBUG

        super().__init__(app)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except Exception as e:
            error_message = format_exc()
            logger.error(error_message)
            unfazed = t.cast(Unfazed, scope.get("app"))

            response: HttpResponse
            if self.debug:
                content = render_error_html(e, unfazed.settings.model_dump())
                response = HtmlResponse(content=content, status_code=500)
            else:
                response = HttpResponse(
                    status_code=500, content="Internal Server Error"
                )
            await response(scope, receive, send)
