Unfazed Serializer
=====

Unfazed 提供一个简单的基于 tortoise-orm model 的序列化器，并提供相应的增删改查方法。


## 快速开始

```python

```python

from tortoise import Model, fields
from unfazed.serializer import Serializer

class Student(Model):
    name = fields.CharField(max_length=255)
    age = fields.IntField()


class StudentSerializer(Serializer):
    class Meta:
        model = Student

# create a student

class StudentCreate(BaseModel):
    name: str
    age: int

StudentSerializer.create_from_ctx(StudentCreate(name="student1", age=18))

# update a student

class StudentUpdate(BaseModel):
    id: int
    name: str
    age: int

StudentSerializer.update_from_ctx(StudentUpdate(id=1, name="student1", age=19))


# delete a student

class StudentDelete(BaseModel):
    id: int

StudentSerializer.destroy_from_ctx(StudentDelete(id=1))

# retrieve a student
class StudentRetrieve(BaseModel):
    id: int

StudentSerializer.retrieve_from_ctx(StudentRetrieve(id=1))


# find relation

class Course(Model):
    name = fields.CharField(max_length=255)
    students = fields.ManyToManyField("models.Student", related_name="courses")

class CourseSerializer(Serializer):
    class Meta:
        model = Course

StudentSerializer.find_relation(CourseSerializer)
    
```



## 高级

### 关系字段初始化

在涉及到关系字段时，`Serializer` 默认不会初始化关系字段，如果需要初始化关系字段，可以通过 `enable_relations` 选项来配置。

```python

class StudentSerializer(Serializer):
    class Meta:
        model = Student
        enable_relations = True

```

但即使配置了 `enable_relations = True`，在初始化时，如果 `tortoise. Tortoise._inited` 还未初始化，`Serializer` 也不会初始化关系字段。

> 参考：https://tortoise.github.io/contrib/pydantic.html

### 参数覆盖

Serializer 支持参数覆盖与新增。

```python

from unfazed.serializer import Serializer
from .models import User

class StudentSerializer(Serializer):
    class Meta:
        model = Student

    age: str
    sex: int


```


### Meta 选项

Serializer 支持 Meta 选项，用于配置 model 与 fields。

```python

from unfazed.serializer import Serializer
from .models import User

class StudentSerializer(Serializer):
    class Meta:
        model = Student
        include = ["name", "age"]

        # 或者 exclude
        # exclude = ["id"]

```

目前 `Serializer` 支持的 Meta 选项如下：

- `include`: 包含的字段
- `exclude`: 排除的字段
- `enable_relations`: 是否启用关系字段

