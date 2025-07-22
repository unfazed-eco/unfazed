v0.0.13
======
- [issue 57](https://github.com/unfazed-eco/unfazed/issues/57) 使用 ipython 实现 shell
- [issue 56](https://github.com/unfazed-eco/unfazed/issues/56) 支持 mount 路由
- [issue 55](https://github.com/unfazed-eco/unfazed/issues/55) 当 app name 与 pkg name 不一致时报错
- [issue 54](https://github.com/unfazed-eco/unfazed/issues/54) 解决 static 路由被 openapi 组件报错的问题


v0.0.12
======

- [issue #39](https://github.com/unfazed-eco/unfazed/issues/39) 增加 `middleware` 在启动时的打印日志
- [issue #44](https://github.com/unfazed-eco/unfazed/issues/44) log 文件名添加 hostname 标识
- [issue #45](https://github.com/unfazed-eco/unfazed/issues/45)  Redis 连接支持连接池相关参数
- [issue #49](https://github.com/unfazed-eco/unfazed/issues/49) 放弃支持 3.0.x，只支持 3.1.x
- [issue #50](https://github.com/unfazed-eco/unfazed/issues/50) Add timer for unfazed setup
- [issue #51](https://github.com/unfazed-eco/unfazed/issues/51) delete useless logs in command

v0.0.11
======

- [issue #37](https://github.com/unfazed-eco/unfazed/issues/37) downgrade openapi to 3.0.x
- [issue #38](https://github.com/unfazed-eco/unfazed/issues/38) add more logs when met error
- [issue #41](https://github.com/unfazed-eco/unfazed/issues/41) fix UploadFile in OpenAPI
- [issue #42](https://github.com/unfazed-eco/unfazed/issues/42) support `alias` in OpenAPI


v0.0.10
======

- [issue #30](https://github.com/unfazed-eco/unfazed/issues/30) add `export_openapi` command
- [issue #31](https://github.com/unfazed-eco/unfazed/issues/31) add `OperationId` in path function
- [issue #32](https://github.com/unfazed-eco/unfazed/issues/32) add `enable_relations` to Serializer Meta class, default is `False`
- [issue #33](https://github.com/unfazed-eco/unfazed/issues/33) opt  TestClient Doc
- [issue #34](https://github.com/unfazed-eco/unfazed/issues/34) add `allow_public` to OpenAPI settings
- [issue #35](https://github.com/unfazed-eco/unfazed/issues/35) add more docs for `CORS`/`GZIP`/`TRUSTED_HOSTS`/`SESSION`

v0.0.9
======

- [issue #28](https://github.com/unfazed-eco/unfazed/issues/28) sys.exit when unfazed setup failed
- [issue #27](https://github.com/unfazed-eco/unfazed/issues/27) fix `t.Annotated[int, p.Query(default=0)]` bug
- change publish workflow name from build to publish
- change all unfazed log level to debug and display unfazed setup summary

v0.0.8
======

- [issue #24](https://github.com/unfazed-eco/unfazed/issues/24) support `order_by` in serializer
- use `unfazed-cli xxx` to replace `python manage.py xxx`
- [issue #22](https://github.com/unfazed-eco/unfazed/issues/22) fix support pydantic 2.11.x


V0.0.7
======

- use cursor to optimize code and add docstring
- fix #17: add `register_settings` to conviniently register settings
- add `Scope`/`Send`/`Receive`/`Scope` in unfazed.type
