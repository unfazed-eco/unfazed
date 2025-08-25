Tortoise ORM 数据库操作
========================

Tortoise ORM 是 Unfazed 框架的默认异步 ORM（对象关系映射）系统，专为 `asyncio` 设计，提供了类似 Django ORM 的简洁 API。它支持多种数据库后端，提供高性能的异步数据库操作能力，是构建现代异步 Web 应用的理想选择。

## 系统概述

### 核心特性

Tortoise ORM 基于 [官方文档](https://tortoise.github.io/) 提供以下核心特性：

- **异步原生**: 完全基于 `asyncio` 构建，提供原生异步数据库操作
- **Django 风格 API**: 熟悉的查询语法和模型定义方式
- **多数据库支持**: 支持 PostgreSQL、MySQL、SQLite、SQL Server、Oracle
- **高性能**: 在基准测试中与其他 Python ORM 相比表现优异
- **类型安全**: 完整的类型注解支持，提供良好的 IDE 体验
- **关系处理**: 支持外键、多对多、一对一等各种关系
- **查询优化**: 支持预加载、聚合、复杂查询等高级功能
- **事务支持**: 完整的事务管理和回滚机制
- **迁移工具**: 与 Aerich 集成的数据库迁移系统

### 支持的数据库

目前 Unfazed 内置支持的驱动有：

| 数据库            | 最低版本 | 驱动        | 连接字符串示例                               |
| ----------------- | -------- | ----------- | -------------------------------------------- |
| **MySQL/MariaDB** | 5.7+     | `asyncmy`   | `mysql://user:pass@host:3306/db`             |
| **SQLite**        | 3.25+    | `aiosqlite` | `sqlite://db.sqlite3` 或 `sqlite://:memory:` |

### 在 Unfazed 中的集成

Unfazed 通过 `ModelCenter` 和 `Driver` 系统无缝集成 Tortoise ORM：

- **自动配置**: 根据 `UNFAZED_SETTINGS` 自动初始化数据库连接
- **应用集成**: 自动发现和注册各应用的模型
- **命令集成**: 内置 Aerich 数据库迁移命令
- **生命周期管理**: 自动处理数据库连接的建立和关闭

## 快速开始

### 基本配置

```python
# settings.py
UNFAZED_SETTINGS = {
    "DEBUG": True,
    "INSTALLED_APPS": [
        "myapp.users",
        "myapp.orders",
        "myapp.products",
    ],
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "tortoise.backends.mysql",
                "CREDENTIALS": {
                    "host": "localhost",
                    "port": 5432,
                    "user": "myapp",
                    "password": "secret",
                    "database": "myapp_db",
                    "minsize": 1,
                    "maxsize": 10,
                }
            }
        },
    }
}
```

### 模型定义

```python
# myapp/users/models.py
from tortoise.models import Model
from tortoise import fields
from typing import Optional
from datetime import datetime

class User(Model):
    """用户模型"""
    id = fields.BigIntField(primary_key=True, description="用户ID")
    username = fields.CharField(max_length=50, unique=True, description="用户名")
    email = fields.CharField(max_length=255, unique=True, description="邮箱")
    password_hash = fields.CharField(max_length=255, description="密码哈希")
    first_name = fields.CharField(max_length=30, description="名")
    last_name = fields.CharField(max_length=30, description="姓")
    is_active = fields.BooleanField(default=True, description="是否激活")
    is_staff = fields.BooleanField(default=False, description="是否员工")
    date_joined = fields.DatetimeField(auto_now_add=True, description="注册时间")
    last_login = fields.DatetimeField(null=True, description="最后登录时间")
    
    # 关系字段
    profile: Optional["UserProfile"]
    orders: fields.ReverseRelation["Order"]
    
    class Meta:
        table = "users"
        indexes = [
            ["username"],
            ["email"],
            ["date_joined"],
        ]
    
    def __str__(self):
        return f"User(username={self.username})"
    
    async def set_password(self, password: str):
        """设置密码"""
        # 实际项目中应使用 bcrypt 等加密
        import hashlib
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    async def check_password(self, password: str) -> bool:
        """验证密码"""
        import hashlib
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

class UserProfile(Model):
    """用户档案模型"""
    id = fields.BigIntField(primary_key=True)
    user = fields.OneToOneField("models.User", related_name="profile", description="关联用户")
    bio = fields.TextField(blank=True, description="个人简介")
    avatar = fields.CharField(max_length=255, null=True, description="头像URL")
    phone = fields.CharField(max_length=20, null=True, description="电话号码")
    address = fields.TextField(blank=True, description="地址")
    birth_date = fields.DateField(null=True, description="生日")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "user_profiles"
```

## 基本 CRUD 操作

### 创建记录

```python
# 创建单个用户
async def create_user():
    user = await User.create(
        username="alice",
        email="alice@example.com",
        first_name="Alice",
        last_name="Smith"
    )
    await user.set_password("secret123")
    await user.save()
    return user

# 批量创建
async def create_multiple_users():
    users_data = [
        {"username": "bob", "email": "bob@example.com", "first_name": "Bob"},
        {"username": "charlie", "email": "charlie@example.com", "first_name": "Charlie"},
    ]
    users = await User.bulk_create([User(**data) for data in users_data])
    return users

# 获取或创建
async def get_or_create_user():
    user, created = await User.get_or_create(
        username="david",
        defaults={
            "email": "david@example.com",
            "first_name": "David"
        }
    )
    return user, created
```

### 查询记录

```python
# 基本查询
async def basic_queries():
    # 获取单个记录
    user = await User.get(username="alice")
    
    # 获取或返回 None
    user = await User.get_or_none(username="nonexistent")
    
    # 获取第一个记录
    first_user = await User.first()
    
    # 过滤查询
    active_users = await User.filter(is_active=True)
    
    # 复杂条件
    recent_users = await User.filter(
        date_joined__gte=datetime(2024, 1, 1),
        is_active=True
    ).exclude(is_staff=True)
    
    # 排序
    users_by_name = await User.all().order_by("first_name", "-date_joined")
    
    # 限制结果
    latest_10_users = await User.all().order_by("-date_joined").limit(10)
    
    # 分页
    page_2_users = await User.all().offset(20).limit(10)

# 高级查询条件
async def advanced_filters():
    # 字符串匹配
    users = await User.filter(username__icontains="alice")  # 忽略大小写包含
    users = await User.filter(email__endswith="@gmail.com")  # 以...结尾
    users = await User.filter(first_name__startswith="A")  # 以...开头
    
    # 数值比较
    users = await User.filter(id__gte=100)  # 大于等于
    users = await User.filter(id__lt=1000)  # 小于
    users = await User.filter(id__in=[1, 2, 3, 4, 5])  # 在列表中
    
    # 日期查询
    from datetime import date, timedelta
    today = date.today()
    users = await User.filter(date_joined__date=today)  # 今天注册
    users = await User.filter(date_joined__year=2024)  # 2024年注册
    users = await User.filter(date_joined__month=12)  # 12月注册
    
    # NULL 查询
    users = await User.filter(last_login__isnull=True)  # 从未登录
    users = await User.filter(last_login__not_isnull=True)  # 已登录过

# 使用 Q 对象进行复杂查询
from tortoise.queryset import Q

async def complex_queries():
    # OR 查询
    users = await User.filter(
        Q(username="alice") | Q(email="alice@example.com")
    )
    
    # AND 查询
    users = await User.filter(
        Q(is_active=True) & Q(is_staff=False)
    )
    
    # NOT 查询
    users = await User.filter(~Q(username="admin"))
    
    # 复杂组合
    users = await User.filter(
        (Q(first_name="Alice") | Q(first_name="Bob")) &
        Q(is_active=True) &
        ~Q(is_staff=True)
    )
```

### 更新记录

```python
async def update_records():
    # 更新单个记录
    user = await User.get(username="alice")
    user.last_login = datetime.now()
    await user.save()
    
    # 批量更新
    await User.filter(is_active=True).update(last_login=datetime.now())
    
    # 条件更新
    updated_count = await User.filter(
        date_joined__lt=datetime(2023, 1, 1)
    ).update(is_active=False)
    
    # 使用 F 表达式
    from tortoise.expressions import F
    await User.all().update(id=F("id") + 1000)
```

### 删除记录

```python
async def delete_records():
    # 删除单个记录
    user = await User.get(username="alice")
    await user.delete()
    
    # 批量删除
    deleted_count = await User.filter(is_active=False).delete()
    
    # 软删除（如果模型支持）
    await User.filter(username="bob").update(is_active=False)
```

## 关系字段操作

### 外键关系 (ForeignKey)

```python
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(Model):
    """订单模型"""
    id = fields.BigIntField(primary_key=True)
    order_number = fields.CharField(max_length=50, unique=True, description="订单号")
    user = fields.ForeignKeyField("models.User", related_name="orders", description="下单用户")
    total_amount = fields.DecimalField(max_digits=10, decimal_places=2, description="总金额")
    status = fields.CharEnumField(OrderStatus, default=OrderStatus.PENDING, description="订单状态")
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    updated_at = fields.DatetimeField(auto_now=True, description="更新时间")
    
    class Meta:
        table = "orders"

async def foreign_key_operations():
    # 创建带关系的记录
    user = await User.create(username="alice", email="alice@example.com")
    
    order = await Order.create(
        order_number="ORD-001",
        user=user,  # 直接传递模型实例
        total_amount=99.99,
        status=OrderStatus.PENDING
    )
    
    # 或者使用 ID
    order = await Order.create(
        order_number="ORD-002",
        user_id=user.id,
        total_amount=149.99,
        status=OrderStatus.PENDING
    )
    
    # 查询时预加载关系
    orders = await Order.filter(status=OrderStatus.PENDING).select_related("user")
    for order in orders:
        print(f"订单 {order.order_number} 属于用户 {order.user.username}")
    
    # 反向查询
    user_orders = await user.orders.all()
    recent_orders = await user.orders.filter(
        created_at__gte=datetime.now() - timedelta(days=30)
    )
```

### 一对一关系 (OneToOne)

```python
async def one_to_one_operations():
    # 创建用户和档案
    user = await User.create(username="bob", email="bob@example.com")
    
    profile = await UserProfile.create(
        user=user,
        bio="Software Developer",
        phone="+1-555-0123",
        birth_date=date(1990, 5, 15)
    )
    
    # 查询时预加载
    user_with_profile = await User.get(username="bob").select_related("profile")
    print(f"用户简介: {user_with_profile.profile.bio}")
    
    # 反向访问
    profile = await UserProfile.get(user__username="bob")
    print(f"档案属于用户: {profile.user.username}")
```

### 多对多关系 (ManyToMany)

```python
class Tag(Model):
    id = fields.BigIntField(primary_key=True)
    name = fields.CharField(max_length=50, unique=True)
    
    class Meta:
        table = "tags"

class Article(Model):
    id = fields.BigIntField(primary_key=True)
    title = fields.CharField(max_length=200)
    content = fields.TextField()
    author = fields.ForeignKeyField("models.User", related_name="articles")
    tags = fields.ManyToManyField("models.Tag", related_name="articles")
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "articles"

async def many_to_many_operations():
    # 创建标签
    tag1 = await Tag.create(name="Python")
    tag2 = await Tag.create(name="异步编程")
    tag3 = await Tag.create(name="Web开发")
    
    # 创建文章
    user = await User.get(username="alice")
    article = await Article.create(
        title="Tortoise ORM 指南",
        content="这是一篇关于 Tortoise ORM 的文章...",
        author=user
    )
    
    # 添加标签
    await article.tags.add(tag1, tag2, tag3)
    
    # 移除标签
    await article.tags.remove(tag3)
    
    # 清空所有标签
    await article.tags.clear()
    
    # 设置标签（替换所有）
    await article.tags.set([tag1, tag2])
    
    # 查询时预加载多对多关系
    articles = await Article.all().prefetch_related("tags", "author")
    for article in articles:
        tag_names = [tag.name for tag in article.tags]
        print(f"文章《{article.title}》标签: {', '.join(tag_names)}")
    
    # 反向查询
    python_articles = await tag1.articles.all()
    
    # 复杂查询
    articles_with_python = await Article.filter(tags__name="Python")
```

## 高级查询功能

### 聚合查询

```python
from tortoise.functions import Count, Sum, Avg, Max, Min

async def aggregation_queries():
    # 计数
    user_count = await User.all().count()
    active_user_count = await User.filter(is_active=True).count()
    
    # 聚合函数
    stats = await Order.all().aggregate(
        total_orders=Count("id"),
        total_revenue=Sum("total_amount"),
        avg_order_value=Avg("total_amount"),
        max_order_value=Max("total_amount"),
        min_order_value=Min("total_amount")
    )
    
    # 分组聚合
    user_order_stats = await Order.all().group_by("user_id").annotate(
        order_count=Count("id"),
        total_spent=Sum("total_amount")
    ).values("user_id", "order_count", "total_spent")
```

### 事务管理

```python
from tortoise.transactions import in_transaction

async def transaction_examples():
    # 使用装饰器
    @in_transaction()
    async def transfer_money(from_user_id: int, to_user_id: int, amount: float):
        # 这些操作将在同一个事务中执行
        from_user = await User.get(id=from_user_id)
        to_user = await User.get(id=to_user_id)
        
        if from_user.balance < amount:
            raise ValueError("余额不足")
        
        from_user.balance -= amount
        to_user.balance += amount
        
        await from_user.save()
        await to_user.save()
    
    # 使用上下文管理器
    async with in_transaction():
        user = await User.create(username="test_user", email="test@example.com")
        profile = await UserProfile.create(user=user, bio="Test bio")
        
        # 如果任何操作失败，整个事务将回滚
        if some_condition:
            raise Exception("回滚事务")
```

## 数据库迁移 (Aerich)

Unfazed 集成了 [Aerich](https://github.com/tortoise/aerich) 作为数据库迁移工具，提供完整的数据库版本控制功能。

### 初始化迁移

```bash
# 初始化 Aerich（首次使用）
unfazed-cli init-db

# 这会创建：
# - migrations/ 目录
# - migrations/models/ 目录
# - 初始迁移文件
```

### 生成迁移文件

```bash
# 检测模型变化并生成迁移文件
unfazed-cli migrate

# 指定迁移名称
unfazed-cli migrate --name add_user_profile

# 生成空的迁移文件（用于手动编写迁移）
unfazed-cli migrate --name custom_migration --empty
```

### 应用迁移

```bash
# 应用所有待执行的迁移
unfazed-cli upgrade

# 在事务中应用迁移
unfazed-cli upgrade --transaction
```

### 回滚迁移

```bash
# 回滚到上一个版本
unfazed-cli downgrade

# 回滚到指定版本
unfazed-cli downgrade --version 2

# 回滚并删除迁移文件
unfazed-cli downgrade --version 1 --delete
```

### 迁移历史管理

```bash
# 查看迁移历史
unfazed-cli history

# 查看待应用的迁移
unfazed-cli heads

# 数据库表结构逆向工程
unfazed-cli inspectdb

# 检查特定表
unfazed-cli inspectdb --table users
```

## 性能优化

### 查询优化

```python
async def query_optimization():
    # 1. 使用 select_related 预加载外键关系
    orders = await Order.all().select_related("user")
    for order in orders:
        print(f"订单 {order.order_number} 用户: {order.user.username}")  # 不会产生 N+1 查询
    
    # 2. 使用 prefetch_related 预加载反向关系和多对多关系
    users = await User.all().prefetch_related("orders", "articles__tags")
    for user in users:
        print(f"用户 {user.username} 有 {len(user.orders)} 个订单")
    
    # 3. 只选择需要的字段
    user_names = await User.all().values_list("username", flat=True)
    user_info = await User.all().values("id", "username", "email")
    
    # 4. 使用索引字段进行查询
    active_users = await User.filter(is_active=True)  # is_active 应该有索引
    
    # 5. 批量操作
    users_data = [
        {"username": f"user_{i}", "email": f"user_{i}@example.com"}
        for i in range(100)
    ]
    await User.bulk_create([User(**data) for data in users_data])
    
    # 6. 使用 exists() 检查存在性
    has_orders = await Order.filter(user_id=1).exists()
```

### 连接池配置

```python
# settings.py - 数据库连接池优化
UNFAZED_SETTINGS = {
    "DATABASE": {
        "CONNECTIONS": {
            "default": {
                "ENGINE": "tortoise.backends.asyncpg",
                "CREDENTIALS": {
                    "host": "localhost",
                    "port": 5432,
                    "user": "myapp",
                    "password": "secret",
                    "database": "myapp_db",
                    # 连接池配置
                    "minsize": 5,        # 最小连接数
                    "maxsize": 20,       # 最大连接数
                    "max_queries": 50000, # 每个连接最大查询数
                    "max_inactive_connection_lifetime": 300,  # 连接最大空闲时间
                    "timeout": 60,       # 连接超时
                    "command_timeout": 60, # 命令超时
                }
            }
        }
    }
}
```

## 测试支持

### 测试数据库配置

```python
# conftest.py
import pytest
from tortoise import Tortoise
from unfazed.core import Unfazed
from unfazed.conf import UnfazedSettings

@pytest.fixture(autouse=True)
async def setup_test_db():
    """设置测试数据库"""
    settings = UnfazedSettings(
        DEBUG=True,
        INSTALLED_APPS=["myapp.users", "myapp.orders"],
        DATABASE={
            "CONNECTIONS": {
                "default": {
                    "ENGINE": "tortoise.backends.sqlite",
                    "CREDENTIALS": {"file_path": ":memory:"}
                }
            },
            "APPS": {
                "models": {
                    "models": ["myapp.users.models", "myapp.orders.models"],
                    "default_connection": "default",
                }
            }
        }
    )
    
    app = Unfazed(settings=settings)
    await app.setup()
    await app.migrate()  # 创建表结构
    
    yield
    
    await Tortoise.close_connections()

@pytest.fixture
async def sample_user():
    """创建测试用户"""
    user = await User.create(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )
    return user
```

### 测试示例

```python
# test_models.py
import pytest
from datetime import datetime, timedelta

async def test_user_creation(sample_user):
    """测试用户创建"""
    assert sample_user.username == "testuser"
    assert sample_user.email == "test@example.com"
    assert sample_user.is_active is True

async def test_user_password():
    """测试密码功能"""
    user = await User.create(
        username="passwordtest",
        email="password@example.com"
    )
    
    await user.set_password("secret123")
    assert await user.check_password("secret123")
    assert not await user.check_password("wrongpassword")

async def test_order_creation(sample_user):
    """测试订单创建"""
    order = await Order.create(
        order_number="TEST-001",
        user=sample_user,
        total_amount=99.99,
        status=OrderStatus.PENDING
    )
    
    assert order.user_id == sample_user.id
    assert order.total_amount == 99.99
    assert order.status == OrderStatus.PENDING

async def test_user_orders_relationship(sample_user):
    """测试用户订单关系"""
    # 创建订单
    order1 = await Order.create(
        order_number="REL-001",
        user=sample_user,
        total_amount=100.00
    )
    order2 = await Order.create(
        order_number="REL-002",
        user=sample_user,
        total_amount=200.00
    )
    
    # 测试反向关系
    user_orders = await sample_user.orders.all()
    assert len(user_orders) == 2
    
    # 测试过滤
    high_value_orders = await sample_user.orders.filter(total_amount__gte=150)
    assert len(high_value_orders) == 1
    assert high_value_orders[0].order_number == "REL-002"
```

## 最佳实践

### 模型设计

```python
# 良好的模型设计示例
class BaseModel(Model):
    """基础模型"""
    id = fields.BigIntField(primary_key=True)
    
    class Meta:
        abstract = True  # 抽象模型

class TimestampedModel(BaseModel):
    """带时间戳的模型"""
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        abstract = True

# 使用继承
class Product(TimestampedModel):
    name = fields.CharField(max_length=255, description="产品名称")
    price = fields.DecimalField(max_digits=10, decimal_places=2, description="价格")
    is_active = fields.BooleanField(default=True, description="是否激活")
    
    class Meta:
        table = "products"
        indexes = [
            ["name"],
            ["is_active", "created_at"],
        ]
```

### 错误处理

```python
from tortoise.exceptions import DoesNotExist, IntegrityError, ValidationError

async def safe_user_operations():
    """安全的用户操作示例"""
    
    try:
        # 尝试创建用户
        user = await User.create(
            username="newuser",
            email="new@example.com"
        )
        return user
        
    except IntegrityError as e:
        # 处理唯一约束违反
        if "username" in str(e):
            raise ValueError("用户名已存在")
        elif "email" in str(e):
            raise ValueError("邮箱已被使用")
        else:
            raise ValueError("数据完整性错误")
    
    except ValidationError as e:
        # 处理验证错误
        raise ValueError(f"数据验证失败: {e}")

async def get_user_safely(user_id: int):
    """安全获取用户"""
    try:
        return await User.get(id=user_id)
    except DoesNotExist:
        return None
```

## 总结

Tortoise ORM 为 Unfazed 应用提供了强大而灵活的数据库操作能力：

**核心优势**：
- 🚀 **异步原生**: 基于 asyncio 的高性能异步操作
- 🎯 **Django 风格**: 熟悉的 API，降低学习成本
- 🔧 **多数据库支持**: 支持主流数据库系统
- 📊 **功能完整**: 从基础 CRUD 到复杂聚合查询
- 🛡️ **生产就绪**: 完整的事务、迁移、测试支持

**关键特性**：
- 完整的关系字段支持（外键、一对一、多对多）
- 高级查询功能（聚合、子查询、原生 SQL）
- 事务管理和嵌套事务
- 数据库迁移工具 Aerich 集成
- 查询优化和性能调优
- 全面的测试支持

通过本文档的指导，您可以充分利用 Tortoise ORM 的强大功能，构建高性能、可维护的数据库驱动应用。

## 参考资源

- **官方文档**: [https://tortoise.github.io/](https://tortoise.github.io/)
- **GitHub 仓库**: [https://github.com/tortoise/tortoise-orm](https://github.com/tortoise/tortoise-orm)
- **Aerich 迁移工具**: [https://github.com/tortoise/aerich](https://github.com/tortoise/aerich)
- **Unfazed 命令系统**: [command.md#aerich](../features/command.md#aerich)
