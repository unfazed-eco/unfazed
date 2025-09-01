![unfazed](images/unfazed-title.png)

<p align="center">
    <em>Production Ready ASGI web framework</em>
</p>



Unfazed
====


Unfazed is an engineering-oriented, async-first, testable, and extensible Python web framework built on [starlette](https://www.starlette.io/), with project organization inspired by [django](https://www.djangoproject.com/).

### Getting Started

1. [Part 1 Installation and Project Creation](tutorial/part1.md)
2. [Part 2 Creating Applications and Hello, World](tutorial/part2.md)
3. [Part 3 Models and Serializers](tutorial/part3.md)
4. [Part 4 Endpoint Functions and Schema Definition](tutorial/part4.md)
5. [Part 5 Business Logic Implementation with Services](tutorial/part5.md)
6. [Part 6 Testing](tutorial/part6.md)

### Features

1. Configuration Module: [settings](features/settings.md) 
2. Application Management: [app](features/app.md)
3. Route Management: [route](features/route.md)
4. Middleware Design: [middleware](features/middleware.md)
5. Lifespan Management: [lifespan](features/lifespan.md)
6. Logging System: [logging](features/logging.md)
7. HTTP Related: [request](features/request.md) | [response](features/response.md)
8. View Function Design: [endpoint](features/endpoint.md)
9. Static File Service: [staticfiles](features/staticfiles.md)
10. Tortoise-orm Related: [ORM](features/tortoise-orm.md) | [Serializer](features/serializer.md)
11. Caching: [cache](features/cache.md)
12. Error Handling: [error](features/error.md)
13. OpenAPI: [openapi](features/openapi.md)
14. Command Line Design: [command](features/command.md)
15. Test Client: [test_client](features/testclient.md)


### Contrib

1. Admin Module: [admin](features/contrib/admin.md)
2. Auth Module: [auth](features/contrib/auth.md)
3. Session Module: [session](features/contrib/session.md)

### Dependencies

Unfazed stands on the shoulders of giants. We thank the following projects:

Unfazed Release Dependencies:

- [starlette](https://www.starlette.io/) provides basic web framework capabilities
- [pydantic](https://pydantic-docs.helpmanual.io/) provides data validation support
- [tortoise-orm](https://tortoise-orm.readthedocs.io/en/latest/) provides ORM support
- [redis](https://redis.io/) provides caching support
- [click](https://click.palletsprojects.com/) provides command-line support
- [jinja2](https://jinja.palletsprojects.com/) provides template support
- [anyio](https://anyio.readthedocs.io/en/stable/) provides async support
- [asgiref](https://asgi.readthedocs.io/en/latest/) provides ASGI support
- [uvicorn](https://www.uvicorn.org/) provides ASGI server support
- [httpx](https://www.python-httpx.org/) provides test client
- [itsdangerous](https://itsdangerous.palletsprojects.com/) provides session support
- [python-multipart](https://github.com/andrew-d/python-multipart) provides multipart/form-data support
- [orjson](https://github.com/ijl/orjson) provides json support
- [aerich](https://github.com/tortoise/aerich) provides ORM migrate support


Unfazed Development Dependencies:

- [mkdocs](https://www.mkdocs.org/) provides documentation support
- [mkdocs-static-i18n](https://github.com/mkdocs/mkdocs-static-i18n) provides multi-language support
- [mypy](https://mypy.readthedocs.io/en/stable/) provides static type checking support
- [ruff](https://github.com/astral-sh/ruff) provides code style checking support
- [pytest](https://docs.pytest.org/en/latest/) provides testing support
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) provides async testing support
- [pytest-cov](https://github.com/pytest-dev/pytest-cov) provides test coverage support
- [asyncmy](https://github.com/asyncmy/asyncmy) provides async mysql support
- [pymysql](https://github.com/PyMySQL/PyMySQL) provides mysql support
- [types-pymysql](https://github.com/python/typeshed) provides mysql type checking support
