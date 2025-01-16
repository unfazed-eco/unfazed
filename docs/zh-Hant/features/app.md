Unfazed APP
============

在 unfazed 项目设计中，不同的业务逻辑模块放到不同的应用中，一个完整的应用包含了

- 视图函数
- 中间件
- 配置
- 路由
- 序列化器
- 模型
- 服务
- 测试

多个应用加上入口配置，就组成了一个完整的 Unfazed 项目。


### 创建应用

在创建项目之后，进入到项目目录，执行 

```bash

python manage.py startapp -n <app_name>

```

创建应用之后，会在项目目录下创建一个应用目录，目录结构如下：



```bash

├── <app_name>
│   ├── admin.py
│   ├── app.py
│   ├── endpoints.py
│   ├── models.py
│   ├── routes.py
│   ├── schema.py
│   ├── serializers.py
│   ├── services.py
│   ├── settings.py
│   └── test_all.py

```

解释一下各个文件的作用：

- admin.py: unfazed 的 admin 配置文件，配合 unfazed-admin 使用
- app.py: app 的入口配置文件
- endpoints.py: app 的接口定义文件
- models.py: app 的数据模型定义文件，unfazed 默认使用 tortoise-orm 作为 ORM
- routes.py: app 的路由定义文件
- schema.py: 接口的请求和响应数据模型定义文件
- serializers.py: 对 model 的序列化和反序列化定义文件
- services.py: 业务逻辑处理文件
- settings.py: 该 app 的配置文件
- test_all.py: 该 app 的测试文件，unfazed 默认使用 pytest 来做测试


### 将应用添加到项目中

使用该应用需要将应用添加到项目配置中

```python

# src/backend/entry/settings/__init__.py

UNFAZED_SETTINGS = {
    "INSTALLED_APPS": [
        "<app_name>",
    ]
}

```

这样才能使应用内的数据模型、命令行工具等被 unfazed 识别。

