Static Files
============

unfazed 提供简单的静态文件服务。


### 快速开始


在项目入口文件夹中的 routes.py 文件中，添加静态文件路由。

```python

# entry/routes.py

from unfazed.route import static

patterns = [
    static("/static", "/tmp/static", html=True)
]

```

假设 /tmp/static 目录如下


```bash

├── css
│   └── bar.css
├── index.html
├── js
│   └── foo.js
└── nested
    └── top
        └── sub
            └── bar.js

```

访问各个文件的 URL 如下

```bash

/static/css/bar.css  -> /tmp/static/css/bar.css
/static/js/foo.js    -> /tmp/static/js/foo.js
/static/index.html   -> /tmp/static/index.html
/static/ -> /tmp/static/index.html
/static/nested/top/sub/bar.js -> /tmp/static/nested/top/sub/bar.js

```


### 函数签名


```python

def static(
    path: str,
    directory: str,
    name: str | None = None,
    html: bool = False,
) -> Static:

```


- path: 静态文件路由路径
- directory: 静态文件目录
- name: 静态文件名称
- html: 未找到对应文件时，是否继续寻找 index.html 文件

