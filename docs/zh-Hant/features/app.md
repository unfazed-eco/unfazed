Unfazed APP
============

## 概述

在 Unfazed 框架中，应用（App）是组织业务逻辑的基本单元。每个应用都是一个独立的模块，包含完整的业务功能实现。一个标准的 Unfazed 应用包含以下组件：

- 视图函数（View Functions）
- 中间件（Middlewares）
- 配置（Configuration）
- 路由（Routes）
- 序列化器（Serializers）
- 数据模型（Models）
- 服务层（Services）
- 测试用例（Tests）

通过组合多个应用并配置入口文件，可以构建一个完整的 Unfazed 项目。

## 创建应用

### 创建命令

在项目根目录下，执行以下命令创建新应用：

```bash
python manage.py startapp -n <app_name>
```

### 应用目录结构

创建应用后，将生成如下目录结构：

```
<app_name>/
├── admin.py        # Admin 管理界面配置
├── app.py          # 应用入口配置
├── endpoints.py    # API 接口定义
├── models.py       # 数据模型定义（使用 Tortoise ORM）
├── routes.py       # 路由配置
├── schema.py       # 接口请求/响应数据模型
├── serializers.py  # 数据序列化/反序列化
├── services.py     # 业务逻辑实现
├── settings.py     # 应用配置
└── test_all.py     # 测试用例（使用 pytest）
```

### 文件说明

| 文件           | 说明                                  |
| -------------- | ------------------------------------- |
| admin.py       | 管理界面配置，配合 unfazed-admin 使用 |
| app.py         | 应用入口配置，定义应用的基本信息      |
| endpoints.py   | API 接口定义，包含接口处理逻辑        |
| models.py      | 数据模型定义，使用 Tortoise ORM       |
| routes.py      | URL 路由配置                          |
| schema.py      | 接口请求和响应的数据模型定义          |
| serializers.py | 数据序列化和反序列化处理              |
| services.py    | 核心业务逻辑实现                      |
| settings.py    | 应用级别的配置项                      |
| test_all.py    | 单元测试和集成测试                    |

## 应用配置

### 注册应用

创建应用后，需要将其添加到项目配置中才能使用。在项目配置文件中添加应用：

```python
# src/backend/entry/settings/__init__.py

UNFAZED_SETTINGS = {
    "INSTALLED_APPS": [
        "<app_name>",  # 添加新创建的应用
    ]
}
```

完成配置后，应用中的模型、命令行工具等功能将被 Unfazed 框架识别和使用。

## 最佳实践

1. 保持应用职责单一，每个应用只负责一个核心功能
2. 合理使用 services.py 处理复杂业务逻辑
3. 编写完整的测试用例确保代码质量
4. 使用 schema.py 严格定义接口数据格式

