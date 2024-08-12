Unfazed development plan
=====



## 功能组件

- [ ] app
- [ ] command
- [ ] conf
- [ ] core
- [ ] http
- [ ] middleware
- [ ] template
- [ ] urls
- [ ] utils
- [ ] contrib
- [ ] db
- [ ] cache
- [ ] log
- [ ] test
- [ ] exception
- [ ] serializer


### apps

apps 包含以下功能

- [ ] AppCenter 集中处理所有的 app，做信息收集与管理
- [ ] AppConfig 用于配置单个 app 的信息


### command

- [ ] CommandCenter 集成处理 internal 命令和 app 中加载的命令
- [ ] 提供 basecommand 类供用户继承，实现自定义命令
- [ ] 提供部分内置命令，如 `runserver` `startproject` `startapp` 等

#### 内置命令

- [ ] runserver
- [ ] startproject
- [ ] startapp


### conf

- [ ] BaseSettings unfazed 需要的基本配置
- [ ] AppSettings 用于配置单个 app 的配置信息


### core

- [ ] Unfazed 用于初始化 unfazed 系统


### http

- [ ] request
- [ ] response

#### request

- [ ] Request 用于封装请求信息


#### response

- [ ] BaseResponse 用于封装响应信息
- [ ] 不同 status code 的 response 类


### middleware

- [ ] clickjacking
- [ ] csrf
- [ ] cors
- [ ] common exception
- [ ] gzip
- [ ] trusted host


### template

- [ ] app template loader
- [ ] project template
- [ ] code template


### route

- [ ] route 处理路由


### utils

- [ ] module_loading
- [ ] 其他还没想好

### contrib

contrib 包含以下的 app

- [ ] admin
- [ ] auth
- [ ] extauth
- [ ] session
- [ ] files
- [ ] openapi
- [ ] serializers
- [ ] generator



### db

- [ ] orm 协议实现
- [ ] 添加一个 ormar backend


### cache

- [ ] local cache 实现
- [ ] cache 协议实现


### log

- [ ] 多进程安全日志处理
- [ ] json 格式日志处理


### test

- [ ] testclient 实现


### exception

- [ ] 基本的 unfazed exception 实现


### serializer

- [ ] 基于 orm 协议的 serializer，用于序列化和反序列化数据，以及固定的 CRUD 操作
