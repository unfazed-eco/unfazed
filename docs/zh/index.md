Unfazed 文档
=======

Unfazed 是一个构建严谨、可维护、可扩展、高性能的 python 异步 web 框架，基于 [starlette](https://www.starlette.io/) 进行开发。


## Unfazed 解决什么问题

- 为什么会有 unfazed
- unfazed 适合什么场景
- unfazed benchmark
- unfazed 架构

## 快速入门

- 安装
- Part1: 创建项目
- Part2: 编写 Models 和 Serializers
- Part3: 编写 Endpoints、 Services 和 Schema
- Part4: Admin 注册
- Part5: 测试

## Unfazed 生态

- unfazed-admin
- unfazed-sentry
- unfazed-prometheus
- unfazed-celery
- unfazed-redis

## Model 层

model

- 简介
- 字段
- 索引
- 元信息
- 关系定义

methods:

- sql vs orm methods
- 关系方法

migrations:

- aerich

other:

- 事务
- 数据库连接池
- 多数据库支持
- 自定义字段


## Serializer 层

- 简介
- 链接 admin
- 链接 services

## Schema 层

- 简介
- reqeust schema
- response schema

## Service 层

- 简介
- 链接 endpoints
- 链接 models
- 链接 serializers

## Endpoint 层

- 简介
- httprequest
- httpresponse | jsonresponse | htmlresponse | streamresponse | fileresponse


## Admin

- 简介
- 注册 model
- 关系处理
- 注册 action


## 其他组件

- caching
- middleware
- command
- settings
- exception
- logging
- lifespan
- test
