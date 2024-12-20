为什么会有 unfazed
=====

在目前 python web 框架生态中，以功能为度来分，可以分为两类：

尽可能包含所有功能的框架

- Django

以仅实现核心功能为目标的框架

- Flask
- FastAPI
- Starlette
- sanic
- blacksheep
- tornado

等等。


以同步为主的框架

- Django
- Flask
- tornado


以异步为主的框架

- FastAPI
- Starlette
- sanic
- blacksheep

等等


可以看到在这里面的缺位是一个以异步为主，但是又包含所有功能的框架，Unfazed 就是为了填补这个缺位而生的。



Unfazed 解决了什么问题
----------------

首先呢，Unfazed 可以看作是异步时代的 Django，它继承了 Django 的一些优点，比如：

1. 统一的 settings 设计
2. 可插拔的 app 设计
3. 好用的 command 工具


在此基础上，Unfazed 又引入了一些新的特性，面向实际的工程开发：

1. 异步为主，有更好的性能
2. 相比 mtv 更加清晰的类 DDD 设计，原生引入 service/serializer/schema 层
3. 相对完善配套的生态，比如 unfazed-admin、unfazed-sentry、unfazed-prometheus、unfazed-celery、unfazed-redis 等等，配合使用可以让项目本身更可靠。


所以，unfazed 的目标是

- 异步为主：更好的性能
- 项目结构清晰：更好的可维护性，可扩展性
- 配套生态完善：日志/报错/监控/异步任务 等等
- 类 django 的设计：可插拔的 app、开发效率高、复用性强


Unfazed 适合什么场景
-------------

结合以上的特点，Unfazed 适合以下几类项目，满足其一即可使用


- qps 在 10000 以内，业务逻辑相对不复杂
- qps 不高的公司内部效率工具
