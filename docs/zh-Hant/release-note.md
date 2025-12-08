v0.0.17
======

- [issue #69](https://github.com/unfazed-eco/unfazed/issues/69) 解决 serializer 没有正确处理 null=true 的情况
- [issue #71](https://github.com/unfazed-eco/unfazed/issues/71) 解决 AdminSite model 缺少的字段
- [issue #73](https://github.com/unfazed-eco/unfazed/issues/73) Auth 模块增加 create-superuser 命令
- [issue #76](https://github.com/unfazed-eco/unfazed/issues/76) 重新整理所有 admin 相关的字段和属性

v0.0.16
======

- 增强了 admin 配置的可定制性
- 更新了认证 endpoints 返回结构化的响应
- 改进静态文件处理 HTML 目录
- 修复测试断言和 admin 模型配置


v0.0.15
======

本次更新完成了对 admin 和 auth 模块的实际实现。

- 重新调整了 admin 和 auth 模块的结构和代码
- [issue 58] 使用 cursor 自动调整了所有文档

v0.0.14
======

本次更新主要修复了 v0.0.13 带出的问题。

1. 移除 run_in_loop 函数以及 loop.call_soon，使用 `loop.run_until_complete` 替代
2. 增加 ipython 未安装的警告
3. 更改模版中的 unfazed 版本号
4. 修复的 admin 组件中 `Model_saveBodyModel` 的 bug
5. 调整部份测试代码



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
