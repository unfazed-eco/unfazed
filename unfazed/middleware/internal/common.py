import typing as t
from traceback import format_exception

import orjson as json
from click.core import Command
from jinja2 import Template

from unfazed.app import BaseAppConfig
from unfazed.http import HtmlResponse, HttpRequest, HttpResponse
from unfazed.middleware.base import BaseHttpMiddleware, RequestResponseEndpoint
from unfazed.protocol import BaseLifeSpan
from unfazed.route import Route


class CommonMiddleware(BaseHttpMiddleware):
    async def dispatch(
        self,
        request: HttpRequest,
        call_next: RequestResponseEndpoint,
    ) -> HttpResponse:
        try:
            response = await call_next(request)
        except Exception as e:
            if self.unfazed.settings.DEBUG:
                response = render_error_html(e, self.unfazed.to_dict())
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
        <pre>{{ unfazed_detail }}</pre>
    </div>
</body>
</html>


"""


def default_dump(obj: t.Any) -> str:
    if isinstance(obj, Route):
        return str(obj)

    elif isinstance(obj, BaseAppConfig):
        return str(obj)

    elif isinstance(obj, BaseHttpMiddleware):
        return str(obj)

    elif isinstance(obj, BaseLifeSpan):
        return str(obj)

    elif isinstance(obj, Command):
        return str(obj)
    else:
        return obj


def render_error_html(
    error: Exception, unfazed_detail: t.Dict[str, t.Any]
) -> HtmlResponse:
    error_content = format_exception(type(error), error, error.__traceback__)
    unfazed_detail_str = json.dumps(unfazed_detail, default=default_dump).decode()

    content = Template(TEMPLATE).render(
        {"error_message": error_content, "unfazed_detail": unfazed_detail_str}
    )

    return HtmlResponse(content=content, status_code=500)
