Unfazed development plan
=====



## 功能组件

- [x] app
- [x] command
- [x] conf
- [x] core
- [ ] http
- [ ] middleware
- [x] template
- [x] route
- [x] utils
- [ ] contrib
- [ ] db
- [x] cache
- [x] log
- [ ] test
- [ ] exception
- [x] serializer
- [ ] type
- [ ] protocol
- [x] openapi
- [ ] schema

### app

app 包含以下功能

- [x] AppCenter 集中处理所有的 app，做信息收集与管理
- [x] AppConfig 用于配置单个 app 的信息


### command

- [x] CommandCenter 集成处理 internal 命令和 app 中加载的命令
- [x] 提供 basecommand 类供用户继承，实现自定义命令
- [x] 提供部分内置命令，如 `runserver` `startproject` `startapp` 等


#### 内置命令

- [x] runserver
- [x] startproject
- [x] startapp


### conf

- [x] BaseSettings unfazed 需要的基本配置
- [x] AppSettings 用于配置单个 app 的配置信息


### core

- [x] Unfazed 用于初始化 unfazed 系统


### http

- [x] request
- [x] response

#### request

- [x] Request 用于封装请求信息


#### response

- [x] BaseResponse 用于封装响应信息
- [x] JsonResponse
- [x] PlainTextResponse
- [x] HtmlResponse
- [x] RedirectResponse
- [ ] FileResponse
- [ ] StreamingResponse


### middleware


- [x] basemiddleware 基础中间件 
- [ ] 默认中间件设计
- [ ] clickjacking
- [ ] csrf
- [ ] cors
- [x] common exception
- [ ] gzip
- [ ] trusted host


### template

- [x] app template loader
- [x] project template
- [ ] code template


### route

- [x] BaseRoute 处理路由
- [x] endpointhandler
- [x] endpointdefinition


### utils

- [x] module_loading

### contrib

contrib 包含以下的 app

- [ ] admin
- [ ] auth
- [ ] extauth
- [ ] session
- [ ] files
- [ ] generator


### db

- [ ] orm 协议实现
- [x] tortoise orm 实现


### cache

- [x] base cache 协议实现
- [x] backend: local cache
- [x] backend: redis


### log

- [x] logcenter 初始化日志
- [x] 多进程安全日志处理
- [x] json 格式日志处理


### test

- [ ] testclient 实现


### exception

- [ ] 基本的 unfazed exception 实现


### serializer

- [x] 基于 orm 协议的 serializer，用于序列化和反序列化数据，以及固定的 CRUD 操作



### openapi

- [x] docs
- [x] redoc


### lifespan

- [ ] lifespan protocol 实现
- [ ] lifespan manager 实现



### type

- [ ] unfazed 常用的 type 实现


### protocol

- [ ] unfazed 常用的 protocol 实现
- [ ] cache
- [ ] command
- [ ] conf
- [ ] lifespan
- [ ] middleware
- [ ] orm
- [ ] route
- [ ] serializer


### schema

- [ ] unfazed 常用的 schema 实现