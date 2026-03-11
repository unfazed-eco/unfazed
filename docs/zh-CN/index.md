Unfazed
====

<p align="center">
    <em>生产就绪的 ASGI Web 框架</em>
</p>

Unfazed 是一个面向工程、异步优先、可测试且可扩展的 Python Web 框架，基于 [starlette](https://www.starlette.io/) 构建，项目组织方式受 [django](https://www.djangoproject.com/) 启发。

### 快速开始

从零开始构建完整的学生选课系统：

1. [第一部分：安装与项目创建](tutorial/part1.md) — 环境配置、项目脚手架、开发服务器
2. [第二部分：创建应用与 Hello World](tutorial/part2.md) — 应用系统、endpoint、路由基础
3. [第三部分：数据模型与 Serializer](tutorial/part3.md) — Tortoise ORM 模型、数据库迁移、CRUD serializer
4. [第四部分：API 接口设计与 Schema 定义](tutorial/part4.md) — 参数注解、请求/响应 schema、OpenAPI 文档
5. [第五部分：业务逻辑实现](tutorial/part5.md) — 服务层、自定义异常、数据库操作
6. [第六部分：测试与质量保障](tutorial/part6.md) — Requestfactory、pytest fixtures、覆盖率

### 功能特性

1. 配置模块：[settings](features/settings.md)
2. 应用管理：[app](features/app.md)
3. 路由管理：[route](features/route.md)
4. 中间件设计：[middleware](features/middleware.md)
5. 生命周期管理：[lifespan](features/lifespan.md)
6. 日志系统：[logging](features/logging.md)
7. HTTP 相关：[request](features/request.md) | [response](features/response.md)
8. 视图函数设计：[endpoint](features/endpoint.md)
9. Tortoise-orm 相关：[ORM](features/tortoise-orm.md) | [Serializer](features/serializer.md)
10. 缓存：[cache](features/cache.md)
11. 异常处理：[exception](features/exception.md)
12. OpenAPI：[openapi](features/openapi.md)
13. 命令行设计：[command](features/command.md)
14. 测试客户端：[test_client](features/testclient.md)


### Contrib

1. Admin 模块：[admin](features/contrib/admin.md)
2. Auth 模块：[auth](features/contrib/auth.md)
3. Session 模块：[session](features/contrib/session.md)

### 依赖项

Unfazed 站在巨人的肩膀上。我们感谢以下项目：

Unfazed 发布依赖：

- [starlette](https://www.starlette.io/) 提供基础 Web 框架能力
- [pydantic](https://pydantic-docs.helpmanual.io/) 提供数据验证支持
- [tortoise-orm](https://tortoise-orm.readthedocs.io/en/latest/) 提供 ORM 支持
- [redis](https://redis.io/) 提供缓存支持
- [click](https://click.palletsprojects.com/) 提供命令行支持
- [jinja2](https://jinja.palletsprojects.com/) 提供模板支持
- [anyio](https://anyio.readthedocs.io/en/stable/) 提供异步支持
- [asgiref](https://asgi.readthedocs.io/en/latest/) 提供 ASGI 支持
- [uvicorn](https://www.uvicorn.org/) 提供 ASGI 服务器支持
- [httpx](https://www.python-httpx.org/) 提供测试客户端
- [itsdangerous](https://itsdangerous.palletsprojects.com/) 提供 session 支持
- [python-multipart](https://github.com/andrew-d/python-multipart) 提供 multipart/form-data 支持
- [orjson](https://github.com/ijl/orjson) 提供 json 支持
- [aerich](https://github.com/tortoise/aerich) 提供 ORM 迁移支持


Unfazed 开发依赖：

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
