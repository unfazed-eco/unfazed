![unfazed](images/unfazed-title.png)

<p align="center">
    <em>Production Ready ASGI web framework</em>
</p>



Unfazed
====


Unfazed 是一个工程导向、异步优先、易测试、易扩展的 Python web 框架，基于 [starlette](https://www.starlette.io/) 开发，项目组织形式向 [django](https://www.djangoproject.com/) 靠拢。

### Unfazed 介绍

1. unfazed 设计理念
2. unfazed 适用场景
3. benchmark
4. DDD vs MTV

### 新手入门

1. [Part 1 安装与创建项目](tutorial/part1.md)
2. [Part 2 创建应用 以及 hello，world](tutorial/part2.md)
3. [Part 3 models 和 序列化器](tutorial/part3.md)
4. [Part 4 endpoint 函数以及 schema 定义](tutorial/part4.md)
5. [Part 5 services 业务逻辑实现](tutorial/part5.md)
6. [Part 6 测试](tutorial/part6.md)

### 特性

1. 配置模块：[settings](features/settings.md) 
2. 中间件设计：[middleware](features/middleware.md)
3. Lifespan 管理：[lifespan](features/lifespan.md)
4. 日志系统：[logging](features/logging.md)
5. HTTP 相关：[request](features/request.md) | [response](features/response.md)
6. 视图函数设计：[endpoint](features/endpoint.md)
7. Tortoise-orm 相关：[ORM](features/tortoise-orm.md) | [Serializer](features/serializer.md)
8. 缓存：[cache](features/cache.md)
9. OPENAPI：[openapi](features/openapi.md)
10. 命令行设计：[command](features/command.md)
11. 测试 client：[test_client](features/testclient.md)


### contrib

1. admin 模块：[admin](features/contrib/admin.md)  - coming soon
2. auth 模块：[auth](features/contrib/auth.md)  - coming soon
3. session 模块：[session](features/contrib/session.md)

### 依赖

unfazed 站在巨人的肩膀上开发，感谢以下项目：

unfazed 发布包依赖：

- [starlette](https://www.starlette.io/) 提供基础 web 框架能力
- [pydantic](https://pydantic-docs.helpmanual.io/) 提供数据验证支持
- [tortoise-orm](https://tortoise-orm.readthedocs.io/en/latest/) 提供 ORM 支持
- [redis](https://redis.io/) 提供缓存支持
- [click](https://click.palletsprojects.com/) 提供命令行支持
- [jinja2](https://jinja.palletsprojects.com/) 提供模板支持
- [anyio](https://anyio.readthedocs.io/en/stable/) 提供异步支持
- [asgiref](https://asgi.readthedocs.io/en/latest/) 提供 ASGI 支持
- [uvicorn](https://www.uvicorn.org/) 提供 ASGI 服务器支持
- [httpx](https://www.python-httpx.org/) 提供测试 client
- [itsdangerous](https://itsdangerous.palletsprojects.com/) 提供 session 支持
- [python-multipart](https://github.com/andrew-d/python-multipart) 提供 multipart/form-data 支持
- [orjson](https://github.com/ijl/orjson) 提供 json 支持
- [aerich](https://github.com/tortoise/aerich) 提供orm migrate支持


unfazed 开发依赖：

- [mkdocs](https://www.mkdocs.org/) 提供文档支持
- [mkdocs-static-i18n](https://github.com/mkdocs/mkdocs-static-i18n) 提供多语言支持
- [mypy](https://mypy.readthedocs.io/en/stable/) 提供静态类型检查支持
- [ruff](https://github.com/astral-sh/ruff) 提供代码风格检查支持
- [pytest](https://docs.pytest.org/en/latest/) 提供测试支持
- [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) 提供异步测试支持
- [pytest-cov](https://github.com/pytest-dev/pytest-cov) 提供测试覆盖率支持
- [asyncmy](https://github.com/asyncmy/asyncmy) 提供异步 mysql 支持
- [pymysql](https://github.com/PyMySQL/PyMySQL) 提供 mysql 支持
- [types-pymysql](https://github.com/python/typeshed) 提供 mysql 类型检查支持

