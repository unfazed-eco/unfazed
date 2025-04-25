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
