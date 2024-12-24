Unfazed Serializer
=====

Unfazed 提供一个简单的基于 tortoise-orm model 的序列化器，并提供相应的增删改查方法。


## 快速开始

```python

# models.py

from tortoise import Model

class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    age = fields.IntField()



# serializers.py

from unfazed.serializer import Serializer
from .models import User


class UserSerializer(Serializer):
    
    class Meta:
        model = User

```

定义完成之后，可以通过以下方式进行增删改查操作。

```python


# services.py


from .serializers import UserSerializer


async def serializer_method():
    # 创建
    user = await UserSerializer.create(name="unfazed", age=18)
    
    # 查询
    user = await UserSerializer.get(id=1)
    
    # 更新
    user = await UserSerializer.update(id=1, name="unfazed2")
    
    # 删除
    user = await UserSerializer.delete(id=1)

```


## 高级

### 参数覆盖

Serializer 支持参数覆盖与新增。

```python

from unfazed.serializer import Serializer
from .models import User

class UserSerializer(Serializer):
    
    class Meta:
        model = User

    # 覆盖 user 中的 age 字段
    age: str

    # 新增 sex 字段
    sex: int 


```


### Meta 选项

Serializer 支持 Meta 选项，用于配置 model 与 fields。

```python

from unfazed.serializer import Serializer
from .models import User

class UserSerializer(Serializer):
    
    class Meta:
        model = User
        include = ["name", "age"]

        # 或者 exclude
        # exclude = ["id"]

```


### 与 tortoise-orm 配合

在涉及到关系字段时，需要特别注意 tortoise-orm 初始化时间

> 参考 https://github.com/tortoise/tortoise-orm/blob/develop/examples/pydantic/early_init.py
> serializer 的初始化一定要放在 tortoise-orm 初始化之后
