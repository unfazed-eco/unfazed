Unfazed Serializer
==================

Unfazed's `Serializer` automatically generates a Pydantic model from a Tortoise ORM model and provides built-in async CRUD operations — create, retrieve, update, delete, and paginated list. It bridges the gap between your database models and your API layer, giving you validated data objects with zero boilerplate.

## Quick Start

### 1. Define a Tortoise model

```python
# myapp/models.py
from tortoise import Model, fields


class Article(Model):
    title = fields.CharField(max_length=255)
    content = fields.TextField()
    published = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
```

### 2. Create a serializer

```python
# myapp/serializers.py
from unfazed.serializer import Serializer
from myapp.models import Article


class ArticleSerializer(Serializer):
    class Meta:
        model = Article
```

`ArticleSerializer` now has Pydantic fields for `id`, `title`, `content`, `published`, and `created_at` — auto-generated from the model.

### 3. Use CRUD operations

```python
from pydantic import BaseModel
from myapp.serializers import ArticleSerializer


class CreateArticle(BaseModel):
    title: str
    content: str


class UpdateArticle(BaseModel):
    id: int
    title: str


# Create
article = await ArticleSerializer.create_from_ctx(
    CreateArticle(title="Hello", content="World")
)

# Retrieve
class ArticleId(BaseModel):
    id: int

article = await ArticleSerializer.retrieve_from_ctx(ArticleId(id=1))

# Update
updated = await ArticleSerializer.update_from_ctx(
    UpdateArticle(id=1, title="Updated Title")
)

# Delete
await ArticleSerializer.destroy_from_ctx(ArticleId(id=1))

# List with pagination
result = await ArticleSerializer.list_from_ctx(
    cond={"published": True},
    page=1,
    size=20,
)
# result.count — total matching records
# result.data  — list of ArticleSerializer instances
```

## The Meta Class

Every serializer must define an inner `Meta` class with at least a `model` attribute:

```python
class ArticleSerializer(Serializer):
    class Meta:
        model = Article
```

### Meta options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `model` | `Type[Model]` | required | The Tortoise ORM model to serialize. |
| `include` | `List[str]` | `[]` | Fields to include. If set, all other fields are excluded. |
| `exclude` | `List[str]` | `[]` | Fields to exclude. Cannot be used together with `include`. |
| `enable_relations` | `bool` | `False` | Generate fields for relation models (FK, M2M, O2O). |

### Controlling fields

By default all model fields are included. Use `include` or `exclude` (but not both) to control which fields appear:

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

## CRUD Operations

All CRUD methods are class methods that accept a Pydantic `BaseModel` context object. The context provides the data for the operation.

### create_from_ctx

```python
article = await ArticleSerializer.create_from_ctx(ctx)
```

Creates a new database record from `ctx` and returns the serialized instance.

### retrieve_from_ctx

```python
article = await ArticleSerializer.retrieve_from_ctx(ctx)
```

Retrieves a record by `ctx.id` and returns the serialized instance.

### update_from_ctx

```python
article = await ArticleSerializer.update_from_ctx(ctx)
```

Finds the record by `ctx.id`, updates the fields present in `ctx`, saves, and returns the serialized instance.

### destroy_from_ctx

```python
await ArticleSerializer.destroy_from_ctx(ctx)
```

Finds the record by `ctx.id` and deletes it.

### list_from_ctx

```python
result = await ArticleSerializer.list_from_ctx(cond, page, size, order_by="-created_at")
```

Queries records matching `cond` (a dict of filter kwargs passed to Tortoise's `.filter()`), paginates the results, and returns a `Result` object.

| Parameter | Type | Description |
|-----------|------|-------------|
| `cond` | `Dict` | Tortoise ORM filter kwargs (e.g. `{"published": True}`). |
| `page` | `int` | Page number (1-based). Pass `0` to disable pagination. |
| `size` | `int` | Page size. |
| `order_by` | `str \| List[str]` | Optional ordering field(s). Prefix with `-` for descending. |
| `fetch_relations` | `bool` | Whether to prefetch related objects. Defaults to `True`. |

Returns a `Result[T]` with `.count` (total) and `.data` (list of serializer instances).

### list_from_queryset

You can also pass a pre-built `QuerySet` instead of a condition dict:

```python
qs = Article.filter(published=True).order_by("-created_at")
result = await ArticleSerializer.list_from_queryset(qs, page=1, size=10)
```

## Relation Support

Set `enable_relations = True` in `Meta` to include relation fields (ForeignKey, ManyToMany, OneToOne, and their backward variants):

```python
class StudentSerializer(Serializer):
    class Meta:
        model = Student
        enable_relations = True
```

**Important:** Relations are only resolved after `Tortoise.init()` has been called. Avoid accessing serializers with `enable_relations = True` inside `app.ready()`. If you need early access, either override the relation field manually or exclude it:

```python
# Option 1: Override with a default
class StudentSerializer(Serializer):
    class Meta:
        model = Student
        enable_relations = True

    courses: list = []

# Option 2: Exclude the relation
class StudentSerializer(Serializer):
    class Meta:
        model = Student
        exclude = ["courses"]
```

### find_relation

Discover the relationship between two serializers:

```python
relation = StudentSerializer.find_relation(CourseSerializer)
# Relation(target="CourseSerializer", source_field="...", target_field="...", relation="m2m")
```

Returns a `Relation` object or `None` if no relationship exists. Supported relation types: `fk`, `m2m`, `o2o`, `bk_fk`, `bk_o2o`.

## Custom Fields

You can add or override fields on a serializer:

```python
from pydantic import Field
from unfazed.serializer import Serializer


class CarSerializer(Serializer):
    override: int = 100
    computed: str = Field(default="custom_value")

    class Meta:
        model = Car
```

Custom fields are merged with the auto-generated fields. If a custom field has the same name as a model field, the custom definition takes precedence.

## API Reference

### Serializer

```python
class Serializer(BaseModel, metaclass=MetaClass)
```

Base class for all serializers. Automatically generates Pydantic fields from the Tortoise model defined in `Meta`.

**Class methods (CRUD):**

- `async create_from_ctx(ctx: BaseModel, **kwargs) -> Self`: Create a record.
- `async update_from_ctx(ctx: BaseModel, **kwargs) -> Self`: Update a record (looks up by `ctx.id`).
- `async destroy_from_ctx(ctx: BaseModel, **kwargs) -> None`: Delete a record (looks up by `ctx.id`).
- `async retrieve_from_ctx(ctx: BaseModel, **kwargs) -> Self`: Retrieve a single record.
- `async list_from_ctx(cond: Dict, page: int, size: int, **kwargs) -> Result[Self]`: List with pagination.
- `async list_from_queryset(queryset: QuerySet, page: int, size: int, **kwargs) -> Result[Self]`: List from a pre-built queryset.

**Class methods (low-level):**

- `from_instance(instance: Model) -> Self`: Create a serializer from a model instance.
- `find_relation(other_cls: Type[Serializer]) -> Relation | None`: Discover relationship between two serializers.
- `get_queryset(cond: Dict, **kwargs) -> QuerySet`: Build a queryset from conditions.
- `get_fetch_fields() -> List[str]`: Return relation fields to prefetch.

**Instance methods:**

- `async create(**kwargs) -> Model`: Insert the serializer's data into the database.
- `async update(instance: Model, **kwargs) -> Model`: Update an existing model instance.
- `async retrieve(instance: Model, **kwargs) -> Self` *(classmethod)*: Fetch relations and return serialized instance.
- `async destroy(instance: Model, **kwargs) -> None` *(classmethod)*: Delete a model instance.
- `valid_data -> Dict`: The subset of fields that can be written to the database.
- `get_write_fields() -> List[str]`: Return writable (non-pk, non-generated, non-auto) field names.

### Result

```python
class Result(BaseModel, Generic[T]):
    count: int
    data: List[T]
```

Pagination result returned by `list_from_ctx` and `list_from_queryset`.

### Relation

```python
class Relation(BaseModel):
    target: str
    source_field: str
    target_field: str
    relation: Literal["fk", "m2m", "o2o", "bk_fk", "bk_o2o"]
```

Describes a relationship between two serializers.
