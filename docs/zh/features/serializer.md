Unfazed Serializer
==================

Unfazed 的 `Serializer` 会从 Tortoise ORM 模型自动生成 Pydantic 模型，并提供内置的异步 CRUD 操作 — 创建、查询、更新、删除和分页列表。它在数据库模型和 API 层之间架起桥梁，让你以零样板代码获得经过验证的数据对象。

## 快速开始

### 1. 定义 Tortoise 模型

```python
# myapp/models.py
from tortoise import Model, fields


class Article(Model):
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    published = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
```

### 2. 创建 serializer

```python
# myapp/serializers.py
from unfazed.serializer import Serializer
from myapp.models import Article


class ArticleSerializer(Serializer):
    class Meta:
        model = Article
```

`ArticleSerializer` 现在拥有 `id`、`title`、`content`、`published` 和 `created_at` 的 Pydantic 字段 — 从模型自动生成。

### 3. 使用 CRUD 操作

```python
from pydantic import BaseModel
from myapp.serializers import ArticleSerializer


class CreateArticle(BaseModel):
    title: str
    content: str


class UpdateArticle(BaseModel):
    id: int
    title: str


# 创建
article = await ArticleSerializer.create_from_ctx(
    CreateArticle(title="Hello", content="World")
)

# 查询
class ArticleId(BaseModel):
    id: int

article = await ArticleSerializer.retrieve_from_ctx(ArticleId(id=1))

# 更新
updated = await ArticleSerializer.update_from_ctx(
    UpdateArticle(id=1, title="Updated Title")
)

# 删除
await ArticleSerializer.destroy_from_ctx(ArticleId(id=1))

# 分页列表
result = await ArticleSerializer.list_from_ctx(
    cond={"published": True},
    page=1,
    size=20,
)
# result.count — 匹配记录总数
# result.data  — ArticleSerializer 实例列表
```

## Meta 类

每个 serializer 必须定义内部 `Meta` 类，并至少包含 `model` 属性：

```python
class ArticleSerializer(Serializer):
    class Meta:
        model = Article
```

### Meta 选项

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | `Type[Model]` | 必填 | 要序列化的 Tortoise ORM 模型。 |
| `include` | `List[str]` | `[]` | 要包含的字段。若设置，则排除其他所有字段。 |
| `exclude` | `List[str]` | `[]` | 要排除的字段。不能与 `include` 同时使用。 |
| `enable_relations` | `bool` | `False` | 是否为关联模型（FK、M2M、O2O）生成字段。 |

### 控制字段

默认包含所有模型字段。使用 `include` 或 `exclude`（二者不可同时使用）控制显示的字段：

```python
class ArticleSummarySerializer(Serializer):
    class Meta:
        model = Article
        include = ["id", "title", "published"]


class ArticleSerializer(Serializer):
    class Meta:
        model = Article
        exclude = ["created_at"]
```

## CRUD 操作

所有 CRUD 方法都是类方法，接受 Pydantic `BaseModel` 上下文对象。上下文提供操作所需的数据。

### create_from_ctx

```python
article = await ArticleSerializer.create_from_ctx(ctx)
```

根据 `ctx` 创建新的数据库记录，并返回序列化后的实例。

### retrieve_from_ctx

```python
article = await ArticleSerializer.retrieve_from_ctx(ctx)
```

根据 `ctx.id` 查询记录，并返回序列化后的实例。

### update_from_ctx

```python
article = await ArticleSerializer.update_from_ctx(ctx)
```

根据 `ctx.id` 查找记录，更新 `ctx` 中存在的字段，保存并返回序列化后的实例。

### destroy_from_ctx

```python
await ArticleSerializer.destroy_from_ctx(ctx)
```

根据 `ctx.id` 查找记录并删除。

### list_from_ctx

```python
result = await ArticleSerializer.list_from_ctx(cond, page, size, order_by="-created_at")
```

查询匹配 `cond`（传给 Tortoise `.filter()` 的过滤参数字典）的记录，对结果分页，并返回 `Result` 对象。

| 参数 | 类型 | 说明 |
|------|------|------|
| `cond` | `Dict` | Tortoise ORM 过滤参数（如 `{"published": True}`）。 |
| `page` | `int` | 页码（从 1 开始）。传 `0` 可禁用分页。 |
| `size` | `int` | 每页大小。 |
| `order_by` | `str \| List[str]` | 可选的排序字段。加 `-` 前缀表示降序。 |
| `fetch_relations` | `bool` | 是否预取关联对象。默认为 `True`。 |

返回包含 `.count`（总数）和 `.data`（serializer 实例列表）的 `Result[T]`。

### list_from_queryset

也可以传入预构建的 `QuerySet` 而非条件字典：

```python
qs = Article.filter(published=True).order_by("-created_at")
result = await ArticleSerializer.list_from_queryset(qs, page=1, size=10)
```

## 关联支持

在 `Meta` 中设置 `enable_relations = True` 可包含关联字段（ForeignKey、ManyToMany、OneToOne 及其反向变体）：

```python
class StudentSerializer(Serializer):
    class Meta:
        model = Student
        enable_relations = True
```

**注意：** 关联只有在调用 `Tortoise.init()` 后才会解析。避免在 `app.ready()` 中访问带有 `enable_relations = True` 的 serializer。如需提前访问，可手动覆盖关联字段或排除它：

```python
# 方式 1：用默认值覆盖
class StudentSerializer(Serializer):
    class Meta:
        model = Student
        enable_relations = True

    courses: list = []

# 方式 2：排除关联
class StudentSerializer(Serializer):
    class Meta:
        model = Student
        exclude = ["courses"]
```

### find_relation

发现两个 serializer 之间的关联关系：

```python
relation = StudentSerializer.find_relation(CourseSerializer)
# Relation(target="CourseSerializer", source_field="...", target_field="...", relation="m2m")
```

返回 `Relation` 对象，若无关联则返回 `None`。支持的关联类型：`fk`、`m2m`、`o2o`、`bk_fk`、`bk_o2o`。

## 自定义字段

可以在 serializer 上添加或覆盖字段：

```python
from pydantic import Field
from unfazed.serializer import Serializer


class CarSerializer(Serializer):
    override: int = 100
    computed: str = Field(default="custom_value")

    class Meta:
        model = Car
```

自定义字段会与自动生成的字段合并。若自定义字段与模型字段同名，则自定义定义优先。

## API 参考

### Serializer

```python
class Serializer(BaseModel, metaclass=MetaClass)
```

所有 serializer 的基类。根据 `Meta` 中定义的 Tortoise 模型自动生成 Pydantic 字段。

**类方法（CRUD）：**

- `async create_from_ctx(ctx: BaseModel, **kwargs) -> Self`: 创建记录。
- `async update_from_ctx(ctx: BaseModel, **kwargs) -> Self`: 更新记录（根据 `ctx.id` 查找）。
- `async destroy_from_ctx(ctx: BaseModel, **kwargs) -> None`: 删除记录（根据 `ctx.id` 查找）。
- `async retrieve_from_ctx(ctx: BaseModel, **kwargs) -> Self`: 查询单条记录。
- `async list_from_ctx(cond: Dict, page: int, size: int, **kwargs) -> Result[Self]`: 分页列表。
- `async list_from_queryset(queryset: QuerySet, page: int, size: int, **kwargs) -> Result[Self]`: 从预构建 queryset 列表。

**类方法（底层）：**

- `from_instance(instance: Model) -> Self`: 从模型实例创建 serializer。
- `find_relation(other_cls: Type[Serializer]) -> Relation | None`: 发现两个 serializer 之间的关联。
- `get_queryset(cond: Dict, **kwargs) -> QuerySet`: 根据条件构建 queryset。
- `get_fetch_fields() -> List[str]`: 返回需要预取的关联字段。

**实例方法：**

- `async create(**kwargs) -> Model`: 将 serializer 数据插入数据库。
- `async update(instance: Model, **kwargs) -> Model`: 更新现有模型实例。
- `async retrieve(instance: Model, **kwargs) -> Self` *(classmethod)*: 获取关联并返回序列化实例。
- `async destroy(instance: Model, **kwargs) -> None` *(classmethod)*: 删除模型实例。
- `valid_data -> Dict`: 可写入数据库的字段子集。
- `get_write_fields() -> List[str]`: 返回可写（非主键、非生成、非自动）字段名。

### Result

```python
class Result(BaseModel, Generic[T]):
    count: int
    data: List[T]
```

由 `list_from_ctx` 和 `list_from_queryset` 返回的分页结果。

### Relation

```python
class Relation(BaseModel):
    target: str
    source_field: str
    target_field: str
    relation: Literal["fk", "m2m", "o2o", "bk_fk", "bk_o2o"]
```

描述两个 serializer 之间的关联关系。
