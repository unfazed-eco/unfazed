Admin
=====

`unfazed.contrib.admin` provides an automatic admin interface for managing your Tortoise ORM models. You register model admins with decorators, and Unfazed serves a JSON API that a frontend (e.g. Ant Design Pro) can consume to render CRUD pages, search panels, inline relations, and custom actions.

## Quick Start

### 1. Install the app, lifespan, and routes

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

### 2. Configure admin settings

```python
# entry/settings/__init__.py

UNFAZED_CONTRIB_ADMIN_SETTINGS = {
    "TITLE": "My Project Admin",
    "API_PREFIX": "/api/contrib/admin",
}
```

### 3. Register a model admin

Create an `admin.py` in your app:

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

The `AdminWakeup` lifespan automatically discovers `admin.py` modules in all installed apps at startup.

## Configuration

Admin settings are registered under `UNFAZED_CONTRIB_ADMIN_SETTINGS`:

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `TITLE` | `str` | `"Unfazed Admin"` | Admin site title. |
| `LOGO` | `str` | Ant Design logo URL | Logo URL. |
| `API_PREFIX` | `str` | `"/api/contrib/admin"` | Prefix for all admin API endpoints. |
| `WEBSITE_PREFIX` | `str` | `"/admin"` | Frontend URL prefix. |
| `TIME_ZONE` | `str` | `"UTC"` | Display timezone. |
| `SHOW_WATERMARK` | `bool` | `True` | Show watermark on the admin site. |
| `DEFAULT_LOGIN_TYPE` | `bool` | `True` | Use default account/password login form. |
| `AUTH_PLUGINS` | `List[AuthPlugin]` | `[]` | OAuth login buttons (each has `ICON_URL` and `PLATFORM`). |
| `ICONFONT_URL` | `str` | `""` | Custom iconfont URL. |
| `EXTRA` | `Dict` | `{}` | Additional config passed to the frontend. |

## Admin API Endpoints

When you include `unfazed.contrib.admin.routes`, the following endpoints are registered:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/route-list` | Return registered admin routes (menu tree). |
| GET | `/settings` | Return site settings (theme, title, logo, etc.). |
| POST | `/model-desc` | Return field definitions and attributes for a model admin. |
| POST | `/model-data` | Query and paginate model data. |
| POST | `/model-inlines` | Return inline relation data for a record. |
| POST | `/model-save` | Create or update a record. |
| POST | `/batch-model-save` | Create or update multiple records in one request. |
| POST | `/model-delete` | Delete a record. |
| POST | `/model-action` | Execute a custom action. |

All endpoints except `/settings` require `@login_required`.

## Admin Classes

### ModelAdmin

The primary admin class for registering a Tortoise model:

```python
@register(PostSerializer)
class PostAdmin(ModelAdmin):
    ...
```

**List page options:**

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `list_display` | `List[str]` | all fields | Columns shown in the list view. |
| `list_sort` | `List[str]` | `[]` | Columns with click-to-sort enabled. |
| `list_search` | `List[str]` | `[]` | Columns with in-table search. |
| `list_filter` | `List[str]` | `[]` | Fields shown as filter options. |
| `list_editable` | `List[str]` | `[]` | Fields editable inline on the list page. |
| `list_order` | `List[str]` | `[]` | Default ordering. |
| `list_per_page` | `int` | `20` | Default page size. |
| `list_per_page_options` | `List[int]` | `[10,20,50,100]` | Page size options. |

**Detail page options:**

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `detail_display` | `List[str]` | all db fields | Fields shown in the detail view. |
| `detail_order` | `List[str]` | `[]` | Display order of fields. |
| `detail_editable` | `List[str]` | `[]` | Editable fields in the detail view. |

**Field type hints:**

| Attribute | Description |
|-----------|-------------|
| `image_fields` | Render as image preview. |
| `datetime_fields` | Render as date/time picker. |
| `editor_fields` | Render as rich-text editor. |
| `json_fields` | Render as JSON editor. |
| `readonly_fields` | Fields that cannot be edited. |
| `not_null_fields` | Fields marked as required. |

**Search panel:**

| Attribute | Description |
|-----------|-------------|
| `search_fields` | Fields shown in the search panel above the table. |
| `search_range_fields` | Subset of `search_fields` rendered as range inputs. |

**Behaviour flags:**

| Attribute | Default | Description |
|-----------|---------|-------------|
| `can_add` | `True` | Show an "Add" button. |
| `can_delete` | `True` | Show a "Delete" button. |
| `can_edit` | `True` | Allow editing records. |
| `can_search` | `True` | Enable the search panel. |
| `can_batch_save` | `True` | Allow batch create/update from the admin UI. |

**Navigation:**

| Attribute | Description |
|-----------|-------------|
| `help_text` | Descriptive text for the admin page. |
| `icon` | Menu icon. |
| `hideInMenu` | Hide from the navigation menu. |
| `hideChildrenInMenu` | Hide child routes. |

### ModelInlineAdmin

Used for related models displayed as inline tables within a parent `ModelAdmin`:

```python
@register(CommentSerializer)
class CommentInlineAdmin(ModelInlineAdmin):
    list_display = ["id", "body", "created_at"]
    max_num = 50
    min_num = 0
```

Wire it to a parent via `inlines`:

```python
from unfazed.contrib.admin.registry import AdminRelation

@register(PostSerializer)
class PostAdmin(ModelAdmin):
    inlines = [
        AdminRelation(target="CommentInlineAdmin"),
    ]
```

Unfazed auto-detects the relation type and join fields when possible (`AutoFill`). For M2M relations, you must provide a `through` configuration with the `AdminThrough` schema.

### Lifecycle Hooks

`ModelAdmin` provides lifecycle hooks around save, batch save, and delete operations:

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

Hook contract:

| Hook | When it runs | Return value |
|------|--------------|--------------|
| `before_save` | Before create/update is executed | Must return the `Serializer` that should be persisted. |
| `after_save` | After create/update succeeds | Returns the saved model instance. |
| `batch_before_save` | Before batch create/update is executed | Must return the serializers that should be persisted. |
| `batch_after_save` | After batch create/update succeeds | Returns the saved model instances. |
| `before_delete` | Before delete is executed | Must return the model instance that should be deleted. |
| `after_delete` | After delete succeeds | Returns the deleted model instance. |

All admin lifecycle hooks must be declared with `async def`. Unlike `@action`, sync hooks are not supported.

`can_batch_save` only controls whether batch save is exposed to the frontend admin. If enabled, the backend batch save endpoint is `POST /batch-model-save`.

### CustomAdmin

For admin pages that are not tied to a model — dashboards, reports, or utility pages:

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

## The @register Decorator

```python
@register(serializer_cls=None)
class MyAdmin(ModelAdmin): ...
```

Registers an admin instance in the global `admin_collector`. Pass a `Serializer` subclass to automatically set the admin's serializer. If the admin class has `override = True`, it replaces any existing registration with the same name.

## The @action Decorator

Define custom actions on admin classes:

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
        # ctx.ids contains selected record IDs
        await Post.filter(id__in=ctx.ids).update(published=True)
        return "Published successfully"
```

**@action parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | method name | Action identifier. |
| `label` | `str` | method name | Display label in the UI. |
| `output` | `ActionOutput` | `Toast` | Output type: `Toast`, `Download`, `Redirect`, etc. |
| `input` | `ActionInput` | `Empty` | Input type: `Empty`, `Text`, `Form`, etc. |
| `confirm` | `bool` | `False` | Show a confirmation dialog before executing. |
| `batch` | `bool` | `False` | Enable batch selection. |
| `description` | `str` | `""` | Tooltip description. |

## Permissions

By default, `BaseAdmin` grants access only to superusers. To use RBAC-based permissions, have your admin classes inherit from `AuthMixin` (from `unfazed.contrib.auth.mixin`):

```python
from unfazed.contrib.auth.mixin import AuthMixin
from unfazed.contrib.admin.registry import ModelAdmin, register


@register(PostSerializer)
class PostAdmin(AuthMixin, ModelAdmin):
    ...
```

This checks `has_view_permission`, `has_change_permission`, etc. against the user's roles and permissions.

## AdminWakeup Lifespan

`AdminWakeup` is a lifespan class that runs on startup. It iterates over all installed apps and calls `app.wakeup("admin")`, which imports each app's `admin.py` module, triggering the `@register` decorators and populating the `admin_collector`.

Add it to your `LIFESPAN` setting:

```python
UNFAZED_SETTINGS = {
    ...
    "LIFESPAN": [
        "unfazed.contrib.admin.registry.lifespan.AdminWakeup",
    ],
}
```
