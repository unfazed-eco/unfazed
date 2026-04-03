Admin
=====

`unfazed.contrib.admin` 为管理 Tortoise ORM 模型提供自动化的 admin 界面。你可以通过装饰器注册模型 admin，Unfazed 会提供 JSON API，供前端（如 Ant Design Pro）消费以渲染 CRUD 页面、搜索面板、内联关联和自定义操作。

## 快速开始

### 1. 安装 app、lifespan 和路由

```python
# entry/settings/__init__.py

UNFAZED_SETTINGS = {
    ...
    "INSTALLED_APPS": [
        "unfazed.contrib.auth",
        "unfazed.contrib.admin",
        "apps.blog",
    ],
    "LIFESPAN": [
        "unfazed.contrib.admin.registry.lifespan.AdminWakeup",
    ],
}
```

```python
# entry/routes.py
from unfazed.route import path, include

patterns = [
    path("/api/contrib/admin", routes=include("unfazed.contrib.admin.routes")),
]
```

### 2. 配置 admin 设置

```python
# entry/settings/__init__.py

UNFAZED_CONTRIB_ADMIN_SETTINGS = {
    "TITLE": "My Project Admin",
    "API_PREFIX": "/api/contrib/admin",
}
```

### 3. 注册模型 admin

在你的 app 中创建 `admin.py`：

```python
# apps/blog/admin.py
from unfazed.contrib.admin.registry import ModelAdmin, register
from apps.blog.serializers import PostSerializer


@register(PostSerializer)
class PostAdmin(ModelAdmin):
    list_display = ["id", "title", "published", "created_at"]
    search_fields = ["title"]
    list_filter = ["published"]
    datetime_fields = ["created_at"]
    readonly_fields = ["id", "created_at"]
```

`AdminWakeup` lifespan 会在启动时自动发现所有已安装 app 中的 `admin.py` 模块。

## 配置

Admin 设置注册在 `UNFAZED_CONTRIB_ADMIN_SETTINGS` 下：

| 键 | 类型 | 默认值 | 描述 |
|-----|------|---------|-------------|
| `TITLE` | `str` | `"Unfazed Admin"` | Admin 站点标题。 |
| `LOGO` | `str` | Ant Design logo URL | Logo URL。 |
| `API_PREFIX` | `str` | `"/api/contrib/admin"` | 所有 admin API endpoint 的前缀。 |
| `WEBSITE_PREFIX` | `str` | `"/admin"` | 前端 URL 前缀。 |
| `TIME_ZONE` | `str` | `"UTC"` | 显示时区。 |
| `SHOW_WATERMARK` | `bool` | `True` | 在 admin 站点显示水印。 |
| `DEFAULT_LOGIN_TYPE` | `bool` | `True` | 使用默认账号/密码登录表单。 |
| `AUTH_PLUGINS` | `List[AuthPlugin]` | `[]` | OAuth 登录按钮（每个包含 `ICON_URL` 和 `PLATFORM`）。 |
| `ICONFONT_URL` | `str` | `""` | 自定义 iconfont URL。 |
| `EXTRA` | `Dict` | `{}` | 传递给前端的额外配置。 |

## Admin API 端点

包含 `unfazed.contrib.admin.routes` 时，会注册以下 endpoint：

| 方法 | 路径 | 描述 |
|--------|------|-------------|
| GET | `/route-list` | 返回已注册的 admin 路由（菜单树）。 |
| GET | `/settings` | 返回站点设置（主题、标题、logo 等）。 |
| POST | `/model-desc` | 返回模型 admin 的字段定义和属性。 |
| POST | `/model-data` | 查询并分页模型数据。 |
| POST | `/model-inlines` | 返回记录的内联关联数据。 |
| POST | `/model-save` | 创建或更新记录。 |
| POST | `/batch-model-save` | 在一次请求中批量创建或更新多条记录。 |
| POST | `/model-delete` | 删除记录。 |
| POST | `/model-action` | 执行自定义操作。 |

除 `/settings` 外，所有 endpoint 均需要 `@login_required`。

## Admin 类

### ModelAdmin

注册 Tortoise 模型的主要 admin 类：

```python
@register(PostSerializer)
class PostAdmin(ModelAdmin):
    ...
```

**列表页选项：**

| 属性 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `list_display` | `List[str]` | 所有字段 | 列表视图中显示的列。 |
| `list_sort` | `List[str]` | `[]` | 启用点击排序的列。 |
| `list_search` | `List[str]` | `[]` | 表内搜索的列。 |
| `list_filter` | `List[str]` | `[]` | 作为筛选选项显示的字段。 |
| `list_editable` | `List[str]` | `[]` | 列表页内联可编辑的字段。 |
| `list_order` | `List[str]` | `[]` | 默认排序。 |
| `list_per_page` | `int` | `20` | 默认每页条数。 |
| `list_per_page_options` | `List[int]` | `[10,20,50,100]` | 每页条数选项。 |

**详情页选项：**

| 属性 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `detail_display` | `List[str]` | 所有 db 字段 | 详情视图中显示的字段。 |
| `detail_order` | `List[str]` | `[]` | 字段显示顺序。 |
| `detail_editable` | `List[str]` | `[]` | 详情视图中可编辑的字段。 |

**字段类型提示：**

| 属性 | 描述 |
|-----------|-------------|
| `image_fields` | 渲染为图片预览。 |
| `datetime_fields` | 渲染为日期/时间选择器。 |
| `editor_fields` | 渲染为富文本编辑器。 |
| `json_fields` | 渲染为 JSON 编辑器。 |
| `readonly_fields` | 不可编辑的字段。 |
| `not_null_fields` | 标记为必填的字段。 |

**搜索面板：**

| 属性 | 描述 |
|-----------|-------------|
| `search_fields` | 表格上方搜索面板中显示的字段。 |
| `search_range_fields` | `search_fields` 的子集，渲染为范围输入。 |

**行为标志：**

| 属性 | 默认值 | 描述 |
|-----------|---------|-------------|
| `can_add` | `True` | 显示「添加」按钮。 |
| `can_delete` | `True` | 显示「删除」按钮。 |
| `can_edit` | `True` | 允许编辑记录。 |
| `can_search` | `True` | 启用搜索面板。 |
| `can_batch_save` | `True` | 允许在 admin 界面中批量创建或更新记录。 |

**导航：**

| 属性 | 描述 |
|-----------|-------------|
| `help_text` | Admin 页面的描述文本。 |
| `icon` | 菜单图标。 |
| `hideInMenu` | 从导航菜单中隐藏。 |
| `hideChildrenInMenu` | 隐藏子路由。 |

### ModelInlineAdmin

用于在父 `ModelAdmin` 内以内联表格形式显示关联模型：

```python
@register(CommentSerializer)
class CommentInlineAdmin(ModelInlineAdmin):
    list_display = ["id", "body", "created_at"]
    max_num = 50
    min_num = 0
```

通过 `inlines` 挂接到父级：

```python
from unfazed.contrib.admin.registry import AdminRelation

@register(PostSerializer)
class PostAdmin(ModelAdmin):
    inlines = [
        AdminRelation(target="CommentInlineAdmin"),
    ]
```

Unfazed 会在可能时自动检测关联类型和连接字段（`AutoFill`）。对于 M2M 关联，你必须使用 `AdminThrough` schema 提供 `through` 配置。

### 生命周期 Hook

`ModelAdmin` 在单条保存、批量保存和删除前后提供生命周期 hook：

```python
from tortoise import Model

from unfazed.contrib.admin.registry import ModelAdmin, register
from unfazed.serializer import Serializer


@register(PostSerializer)
class PostAdmin(ModelAdmin):
    async def before_save(self, serializer: Serializer, **kwargs) -> Serializer:
        serializer.title = serializer.title.strip()
        return serializer

    async def after_save(self, instance: Model, **kwargs) -> Model:
        return instance

    async def batch_before_save(
        self, serializers: list[Serializer], **kwargs
    ) -> list[Serializer]:
        return serializers

    async def batch_after_save(
        self, instances: list[Model], **kwargs
    ) -> list[Model]:
        return instances

    async def before_delete(self, instance: Model, **kwargs) -> Model:
        return instance

    async def after_delete(self, instance: Model, **kwargs) -> Model:
        return instance
```

Hook 约定如下：

| Hook | 执行时机 | 返回值 |
|------|----------|--------|
| `before_save` | 在创建/更新真正执行前 | 必须返回要落库的 `Serializer`。 |
| `after_save` | 在创建/更新成功后 | 返回已保存的模型实例。 |
| `batch_before_save` | 在批量创建/更新真正执行前 | 必须返回要落库的 serializers。 |
| `batch_after_save` | 在批量创建/更新成功后 | 返回已保存的模型实例列表。 |
| `before_delete` | 在删除真正执行前 | 必须返回要删除的模型实例。 |
| `after_delete` | 在删除成功后 | 返回已删除的模型实例。 |

所有 admin 生命周期 hook 都必须使用 `async def` 定义。和 `@action` 不同，同步 hook 当前不受支持。

`can_batch_save` 只控制前端 admin 是否暴露批量保存能力；启用后，后端对应的批量保存 endpoint 是 `POST /batch-model-save`。

### CustomAdmin

用于不绑定模型的 admin 页面 — 仪表盘、报表或工具页：

```python
from unfazed.contrib.admin.registry import CustomAdmin, register, action, ActionOutput
from unfazed.contrib.admin.registry.fields import Field


@register()
class DashboardAdmin(CustomAdmin):
    component = "ModelCustom"
    fields_set = [
        Field(name="date_range", field_type="DatetimeField"),
    ]

    @action(name="export_report", label="Export Report", output=ActionOutput.Download)
    async def export_report(self, ctx):
        ...
```

## @register 装饰器

```python
@register(serializer_cls=None)
class MyAdmin(ModelAdmin): ...
```

在全局 `admin_collector` 中注册 admin 实例。传入 `Serializer` 子类可自动设置 admin 的 serializer。若 admin 类有 `override = True`，则替换同名已有注册。

## @action 装饰器

在 admin 类上定义自定义操作：

```python
from unfazed.contrib.admin.registry import action, ActionOutput, ActionInput, ActionKwargs


@register(PostSerializer)
class PostAdmin(ModelAdmin):

    @action(
        name="publish",
        label="Publish Selected",
        output=ActionOutput.Toast,
        confirm=True,
        batch=True,
    )
    async def publish(self, ctx: ActionKwargs) -> str:
        # ctx.ids 包含选中的记录 ID
        await Post.filter(id__in=ctx.ids).update(published=True)
        return "Published successfully"
```

**@action 参数：**

| 参数 | 类型 | 默认值 | 描述 |
|-----------|------|---------|-------------|
| `name` | `str` | 方法名 | 操作标识符。 |
| `label` | `str` | 方法名 | UI 中的显示标签。 |
| `output` | `ActionOutput` | `Toast` | 输出类型：`Toast`、`Download`、`Redirect` 等。 |
| `input` | `ActionInput` | `Empty` | 输入类型：`Empty`、`Text`、`Form` 等。 |
| `confirm` | `bool` | `False` | 执行前显示确认对话框。 |
| `batch` | `bool` | `False` | 启用批量选择。 |
| `description` | `str` | `""` | 工具提示描述。 |

## 权限

默认情况下，`BaseAdmin` 仅授予超级用户访问权限。若要使用基于 RBAC 的权限，让 admin 类继承自 `AuthMixin`（来自 `unfazed.contrib.auth.mixin`）：

```python
from unfazed.contrib.auth.mixin import AuthMixin
from unfazed.contrib.admin.registry import ModelAdmin, register


@register(PostSerializer)
class PostAdmin(AuthMixin, ModelAdmin):
    ...
```

这会根据用户的角色和权限检查 `has_view_permission`、`has_change_permission` 等。

## AdminWakeup Lifespan

`AdminWakeup` 是在启动时运行的 lifespan 类。它会遍历所有已安装的 app 并调用 `app.wakeup("admin")`，从而导入每个 app 的 `admin.py` 模块，触发 `@register` 装饰器并填充 `admin_collector`。

将其添加到 `LIFESPAN` 设置中：

```python
UNFAZED_SETTINGS = {
    ...
    "LIFESPAN": [
        "unfazed.contrib.admin.registry.lifespan.AdminWakeup",
    ],
}
```
