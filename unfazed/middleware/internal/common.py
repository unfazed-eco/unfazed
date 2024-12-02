import typing as t
from traceback import format_exception

import orjson as json
from jinja2 import Template

from unfazed.core import Unfazed
from unfazed.http import HtmlResponse, HttpRequest, HttpResponse
from unfazed.middleware.base import BaseHttpMiddleware, RequestResponseEndpoint


class CommonMiddleware(BaseHttpMiddleware):
    async def dispatch(
        self,
        request: HttpRequest,
        call_next: RequestResponseEndpoint,
    ) -> HttpResponse:
        try:
            response = await call_next(request)
        except Exception as e:
            unfazed: Unfazed = request.scope.get("app")
            if unfazed.settings.DEBUG:
                response = render_error_html(e, unfazed.settings.model_dump())
            else:
                response = HttpResponse(
                    status_code=500, content="Internal Server Error"
                )
        return response


TEMPLATE = """

<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UNFAZED ERROR PAGE</title>
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
    <div class="container">
        <h1>ERROR</h1>
        <h2>TRACEBACK</h2>
        <pre>{{ error_message }}</pre>
    </div>

    <div class="container">
        <h1>UNFAZED DETAIL</h1>
        <pre>{{ unfazed_settings }}</pre>
    </div>
</body>
</html>


"""


def render_error_html(
    error: Exception, unfazed_settings: t.Dict[str, t.Any]
) -> HtmlResponse:
    error_content = format_exception(type(error), error, error.__traceback__)
    unfazed_settings_str = json.dumps(unfazed_settings).decode()

    content = Template(TEMPLATE).render(
        {"error_message": error_content, "unfazed_settings": unfazed_settings_str}
    )

    return HtmlResponse(content=content, status_code=500)
