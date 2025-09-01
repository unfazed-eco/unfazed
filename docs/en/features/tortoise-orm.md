Tortoise ORM Database Operations
========================

Tortoise ORM is Unfazed framework's default async ORM (Object-Relational Mapping) system, designed specifically for `asyncio`, providing a Django ORM-like concise API. It supports multiple database backends, providing high-performance async database operation capabilities, making it an ideal choice for building modern async Web applications.

## System Overview

### Core Features

Tortoise ORM provides the following core features based on [official documentation](https://tortoise.github.io/):

- **Async Native**: Completely built on `asyncio`, providing native async database operations
- **Django-style API**: Familiar query syntax and model definition approach
- **Multi-database Support**: Supports PostgreSQL, MySQL, SQLite, SQL Server, Oracle
- **High Performance**: Excellent performance in benchmarks compared to other Python ORMs
- **Type Safety**: Complete type annotation support, providing good IDE experience
- **Relationship Handling**: Supports foreign keys, many-to-many, one-to-one, and other relationships
- **Query Optimization**: Supports preloading, aggregation, complex queries, and other advanced features
- **Transaction Support**: Complete transaction management and rollback mechanisms
- **Migration Tools**: Database migration system integrated with Aerich

### Supported Databases

Currently, Unfazed has built-in support for the following drivers:

| Database          | Minimum Version | Driver      | Connection String Example                    |
| ----------------- | --------------- | ----------- | -------------------------------------------- |
| **MySQL/MariaDB** | 5.7+            | `asyncmy`   | `mysql://user:pass@host:3306/db`             |
| **SQLite**        | 3.25+           | `aiosqlite` | `sqlite://db.sqlite3` or `sqlite://:memory:` |

### Integration in Unfazed

Unfazed seamlessly integrates Tortoise ORM through `ModelCenter` and `Driver` systems:

- **Auto Configuration**: Automatically initializes database connections based on `UNFAZED_SETTINGS`
- **Application Integration**: Automatically discovers and registers models from each application
- **Command Integration**: Built-in Aerich database migration commands
- **Lifecycle Management**: Automatically handles database connection establishment and closure

## Quick Start

### Basic Configuration

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

### Model Definition

```python
# myapp/users/models.py
from tortoise.models import Model
from tortoise import fields
from typing import Optional
from datetime import datetime

class User(Model):
    """User model"""
    id = fields.BigIntField(primary_key=True, description="User ID")
    username = fields.CharField(max_length=50, unique=True, description="Username")
    email = fields.CharField(max_length=255, unique=True, description="Email")
    password_hash = fields.CharField(max_length=255, description="Password hash")
    first_name = fields.CharField(max_length=30, description="First name")
    last_name = fields.CharField(max_length=30, description="Last name")
    is_active = fields.BooleanField(default=True, description="Is active")
    is_staff = fields.BooleanField(default=False, description="Is staff")
    date_joined = fields.DatetimeField(auto_now_add=True, description="Registration time")
    last_login = fields.DatetimeField(null=True, description="Last login time")
    
    # Relationship fields
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
        """Set password"""
        # In real projects, should use bcrypt or other encryption
        import hashlib
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    async def check_password(self, password: str) -> bool:
        """Verify password"""
        import hashlib
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

class UserProfile(Model):
    """User profile model"""
    id = fields.BigIntField(primary_key=True)
    user = fields.OneToOneField("models.User", related_name="profile", description="Associated user")
    bio = fields.TextField(blank=True, description="Personal bio")
    avatar = fields.CharField(max_length=255, null=True, description="Avatar URL")
    phone = fields.CharField(max_length=20, null=True, description="Phone number")
    address = fields.TextField(blank=True, description="Address")
    birth_date = fields.DateField(null=True, description="Birth date")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "user_profiles"
```

## Basic CRUD Operations

### Create Records

```python
# Create single user
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

# Batch create
async def create_multiple_users():
    users_data = [
        {"username": "bob", "email": "bob@example.com", "first_name": "Bob"},
        {"username": "charlie", "email": "charlie@example.com", "first_name": "Charlie"},
    ]
    users = await User.bulk_create([User(**data) for data in users_data])
    return users

# Get or create
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

### Query Records

```python
# Basic queries
async def basic_queries():
    # Get single record
    user = await User.get(username="alice")
    
    # Get or return None
    user = await User.get_or_none(username="nonexistent")
    
    # Get first record
    first_user = await User.first()
    
    # Filter queries
    active_users = await User.filter(is_active=True)
    
    # Complex conditions
    recent_users = await User.filter(
        date_joined__gte=datetime(2024, 1, 1),
        is_active=True
    ).exclude(is_staff=True)
    
    # Sorting
    users_by_name = await User.all().order_by("first_name", "-date_joined")
    
    # Limit results
    latest_10_users = await User.all().order_by("-date_joined").limit(10)
    
    # Pagination
    page_2_users = await User.all().offset(20).limit(10)

# Advanced query conditions
async def advanced_filters():
    # String matching
    users = await User.filter(username__icontains="alice")  # Case-insensitive contains
    users = await User.filter(email__endswith="@gmail.com")  # Ends with
    users = await User.filter(first_name__startswith="A")  # Starts with
    
    # Numeric comparison
    users = await User.filter(id__gte=100)  # Greater than or equal
    users = await User.filter(id__lt=1000)  # Less than
    users = await User.filter(id__in=[1, 2, 3, 4, 5])  # In list
    
    # Date queries
    from datetime import date, timedelta
    today = date.today()
    users = await User.filter(date_joined__date=today)  # Registered today
    users = await User.filter(date_joined__year=2024)  # Registered in 2024
    users = await User.filter(date_joined__month=12)  # Registered in December
    
    # NULL queries
    users = await User.filter(last_login__isnull=True)  # Never logged in
    users = await User.filter(last_login__not_isnull=True)  # Has logged in

# Use Q objects for complex queries
from tortoise.queryset import Q

async def complex_queries():
    # OR query
    users = await User.filter(
        Q(username="alice") | Q(email="alice@example.com")
    )
    
    # AND query
    users = await User.filter(
        Q(is_active=True) & Q(is_staff=False)
    )
    
    # NOT query
    users = await User.filter(~Q(username="admin"))
    
    # Complex combination
    users = await User.filter(
        (Q(first_name="Alice") | Q(first_name="Bob")) &
        Q(is_active=True) &
        ~Q(is_staff=True)
    )
```

### Update Records

```python
async def update_records():
    # Update single record
    user = await User.get(username="alice")
    user.last_login = datetime.now()
    await user.save()
    
    # Batch update
    await User.filter(is_active=True).update(last_login=datetime.now())
    
    # Conditional update
    updated_count = await User.filter(
        date_joined__lt=datetime(2023, 1, 1)
    ).update(is_active=False)
    
    # Use F expressions
    from tortoise.expressions import F
    await User.all().update(id=F("id") + 1000)
```

### Delete Records

```python
async def delete_records():
    # Delete single record
    user = await User.get(username="alice")
    await user.delete()
    
    # Batch delete
    deleted_count = await User.filter(is_active=False).delete()
    
    # Soft delete (if model supports)
    await User.filter(username="bob").update(is_active=False)
```

## Relationship Field Operations

### Foreign Key Relationships (ForeignKey)

```python
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(Model):
    """Order model"""
    id = fields.BigIntField(primary_key=True)
    order_number = fields.CharField(max_length=50, unique=True, description="Order number")
    user = fields.ForeignKeyField("models.User", related_name="orders", description="Ordering user")
    total_amount = fields.DecimalField(max_digits=10, decimal_places=2, description="Total amount")
    status = fields.CharEnumField(OrderStatus, default=OrderStatus.PENDING, description="Order status")
    created_at = fields.DatetimeField(auto_now_add=True, description="Created at")
    updated_at = fields.DatetimeField(auto_now=True, description="Updated at")
    
    class Meta:
        table = "orders"

async def foreign_key_operations():
    # Create records with relationships
    user = await User.create(username="alice", email="alice@example.com")
    
    order = await Order.create(
        order_number="ORD-001",
        user=user,  # Pass model instance directly
        total_amount=99.99,
        status=OrderStatus.PENDING
    )
    
    # Or use ID
    order = await Order.create(
        order_number="ORD-002",
        user_id=user.id,
        total_amount=149.99,
        status=OrderStatus.PENDING
    )
    
    # Preload relationships when querying
    orders = await Order.filter(status=OrderStatus.PENDING).select_related("user")
    for order in orders:
        print(f"Order {order.order_number} belongs to user {order.user.username}")
    
    # Reverse query
    user_orders = await user.orders.all()
    recent_orders = await user.orders.filter(
        created_at__gte=datetime.now() - timedelta(days=30)
    )
```

### One-to-One Relationships (OneToOne)

```python
async def one_to_one_operations():
    # Create user and profile
    user = await User.create(username="bob", email="bob@example.com")
    
    profile = await UserProfile.create(
        user=user,
        bio="Software Developer",
        phone="+1-555-0123",
        birth_date=date(1990, 5, 15)
    )
    
    # Preload when querying
    user_with_profile = await User.get(username="bob").select_related("profile")
    print(f"User bio: {user_with_profile.profile.bio}")
    
    # Reverse access
    profile = await UserProfile.get(user__username="bob")
    print(f"Profile belongs to user: {profile.user.username}")
```

### Many-to-Many Relationships (ManyToMany)

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
    # Create tags
    tag1 = await Tag.create(name="Python")
    tag2 = await Tag.create(name="Async Programming")
    tag3 = await Tag.create(name="Web Development")
    
    # Create article
    user = await User.get(username="alice")
    article = await Article.create(
        title="Tortoise ORM Guide",
        content="This is an article about Tortoise ORM...",
        author=user
    )
    
    # Add tags
    await article.tags.add(tag1, tag2, tag3)
    
    # Remove tags
    await article.tags.remove(tag3)
    
    # Clear all tags
    await article.tags.clear()
    
    # Set tags (replace all)
    await article.tags.set([tag1, tag2])
    
    # Preload many-to-many relationships when querying
    articles = await Article.all().prefetch_related("tags", "author")
    for article in articles:
        tag_names = [tag.name for tag in article.tags]
        print(f"Article '{article.title}' tags: {', '.join(tag_names)}")
    
    # Reverse query
    python_articles = await tag1.articles.all()
    
    # Complex query
    articles_with_python = await Article.filter(tags__name="Python")
```

## Advanced Query Features

### Aggregation Queries

```python
from tortoise.functions import Count, Sum, Avg, Max, Min

async def aggregation_queries():
    # Count
    user_count = await User.all().count()
    active_user_count = await User.filter(is_active=True).count()
    
    # Aggregation functions
    stats = await Order.all().aggregate(
        total_orders=Count("id"),
        total_revenue=Sum("total_amount"),
        avg_order_value=Avg("total_amount"),
        max_order_value=Max("total_amount"),
        min_order_value=Min("total_amount")
    )
    
    # Group aggregation
    user_order_stats = await Order.all().group_by("user_id").annotate(
        order_count=Count("id"),
        total_spent=Sum("total_amount")
    ).values("user_id", "order_count", "total_spent")
```

### Transaction Management

```python
from tortoise.transactions import in_transaction

async def transaction_examples():
    # Use decorator
    @in_transaction()
    async def transfer_money(from_user_id: int, to_user_id: int, amount: float):
        # These operations will be executed in the same transaction
        from_user = await User.get(id=from_user_id)
        to_user = await User.get(id=to_user_id)
        
        if from_user.balance < amount:
            raise ValueError("Insufficient balance")
        
        from_user.balance -= amount
        to_user.balance += amount
        
        await from_user.save()
        await to_user.save()
    
    # Use context manager
    async with in_transaction():
        user = await User.create(username="test_user", email="test@example.com")
        profile = await UserProfile.create(user=user, bio="Test bio")
        
        # If any operation fails, the entire transaction will rollback
        if some_condition:
            raise Exception("Rollback transaction")
```

## Database Migration (Aerich)

Unfazed integrates [Aerich](https://github.com/tortoise/aerich) as a database migration tool, providing complete database version control functionality.

### Initialize Migration

```bash
# Initialize Aerich (first time use)
unfazed-cli init-db

# This creates:
# - migrations/ directory
# - migrations/models/ directory
# - Initial migration files
```

### Generate Migration Files

```bash
# Detect model changes and generate migration files
unfazed-cli migrate

# Specify migration name
unfazed-cli migrate --name add_user_profile

# Generate empty migration file (for manual migration writing)
unfazed-cli migrate --name custom_migration --empty
```

### Apply Migrations

```bash
# Apply all pending migrations
unfazed-cli upgrade

# Apply migrations in transaction
unfazed-cli upgrade --transaction
```

### Rollback Migrations

```bash
# Rollback to previous version
unfazed-cli downgrade

# Rollback to specified version
unfazed-cli downgrade --version 2

# Rollback and delete migration files
unfazed-cli downgrade --version 1 --delete
```

### Migration History Management

```bash
# View migration history
unfazed-cli history

# View pending migrations
unfazed-cli heads

# Database table structure reverse engineering
unfazed-cli inspectdb

# Check specific table
unfazed-cli inspectdb --table users
```

## Performance Optimization

### Query Optimization

```python
async def query_optimization():
    # 1. Use select_related to preload foreign key relationships
    orders = await Order.all().select_related("user")
    for order in orders:
        print(f"Order {order.order_number} user: {order.user.username}")  # Won't cause N+1 queries
    
    # 2. Use prefetch_related to preload reverse relationships and many-to-many relationships
    users = await User.all().prefetch_related("orders", "articles__tags")
    for user in users:
        print(f"User {user.username} has {len(user.orders)} orders")
    
    # 3. Only select needed fields
    user_names = await User.all().values_list("username", flat=True)
    user_info = await User.all().values("id", "username", "email")
    
    # 4. Use indexed fields for queries
    active_users = await User.filter(is_active=True)  # is_active should have index
    
    # 5. Batch operations
    users_data = [
        {"username": f"user_{i}", "email": f"user_{i}@example.com"}
        for i in range(100)
    ]
    await User.bulk_create([User(**data) for data in users_data])
    
    # 6. Use exists() to check existence
    has_orders = await Order.filter(user_id=1).exists()
```

### Connection Pool Configuration

```python
# settings.py - Database connection pool optimization
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
                    # Connection pool configuration
                    "minsize": 5,        # Minimum connections
                    "maxsize": 20,       # Maximum connections
                    "max_queries": 50000, # Maximum queries per connection
                    "max_inactive_connection_lifetime": 300,  # Maximum connection idle time
                    "timeout": 60,       # Connection timeout
                    "command_timeout": 60, # Command timeout
                }
            }
        }
    }
}
```

## Test Support

### Test Database Configuration

```python
# conftest.py
import pytest
from tortoise import Tortoise
from unfazed.core import Unfazed
from unfazed.conf import UnfazedSettings

@pytest.fixture(autouse=True)
async def setup_test_db():
    """Setup test database"""
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
    await app.migrate()  # Create table structure
    
    yield
    
    await Tortoise.close_connections()

@pytest.fixture
async def sample_user():
    """Create test user"""
    user = await User.create(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User"
    )
    return user
```

### Test Examples

```python
# test_models.py
import pytest
from datetime import datetime, timedelta

async def test_user_creation(sample_user):
    """Test user creation"""
    assert sample_user.username == "testuser"
    assert sample_user.email == "test@example.com"
    assert sample_user.is_active is True

async def test_user_password():
    """Test password functionality"""
    user = await User.create(
        username="passwordtest",
        email="password@example.com"
    )
    
    await user.set_password("secret123")
    assert await user.check_password("secret123")
    assert not await user.check_password("wrongpassword")

async def test_order_creation(sample_user):
    """Test order creation"""
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
    """Test user orders relationship"""
    # Create orders
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
    
    # Test reverse relationship
    user_orders = await sample_user.orders.all()
    assert len(user_orders) == 2
    
    # Test filtering
    high_value_orders = await sample_user.orders.filter(total_amount__gte=150)
    assert len(high_value_orders) == 1
    assert high_value_orders[0].order_number == "REL-002"
```

## Best Practices

### Model Design

```python
# Good model design example
class BaseModel(Model):
    """Base model"""
    id = fields.BigIntField(primary_key=True)
    
    class Meta:
        abstract = True  # Abstract model

class TimestampedModel(BaseModel):
    """Model with timestamps"""
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        abstract = True

# Use inheritance
class Product(TimestampedModel):
    name = fields.CharField(max_length=255, description="Product name")
    price = fields.DecimalField(max_digits=10, decimal_places=2, description="Price")
    is_active = fields.BooleanField(default=True, description="Is active")
    
    class Meta:
        table = "products"
        indexes = [
            ["name"],
            ["is_active", "created_at"],
        ]
```

### Error Handling

```python
from tortoise.exceptions import DoesNotExist, IntegrityError, ValidationError

async def safe_user_operations():
    """Safe user operations example"""
    
    try:
        # Try to create user
        user = await User.create(
            username="newuser",
            email="new@example.com"
        )
        return user
        
    except IntegrityError as e:
        # Handle unique constraint violations
        if "username" in str(e):
            raise ValueError("Username already exists")
        elif "email" in str(e):
            raise ValueError("Email already in use")
        else:
            raise ValueError("Data integrity error")
    
    except ValidationError as e:
        # Handle validation errors
        raise ValueError(f"Data validation failed: {e}")

async def get_user_safely(user_id: int):
    """Safely get user"""
    try:
        return await User.get(id=user_id)
    except DoesNotExist:
        return None
```

## Summary

Tortoise ORM provides Unfazed applications with powerful and flexible database operation capabilities:

**Core Advantages**:
- 🚀 **Async Native**: High-performance async operations based on asyncio
- 🎯 **Django Style**: Familiar API, reducing learning curve
- 🔧 **Multi-database Support**: Supports mainstream database systems
- 📊 **Complete Features**: From basic CRUD to complex aggregation queries
- 🛡️ **Production Ready**: Complete transaction, migration, and test support

**Key Features**:
- Complete relationship field support (foreign keys, one-to-one, many-to-many)
- Advanced query features (aggregation, subqueries, raw SQL)
- Transaction management and nested transactions
- Database migration tool Aerich integration
- Query optimization and performance tuning
- Comprehensive test support

Through this documentation's guidance, you can fully utilize Tortoise ORM's powerful features to build high-performance, maintainable database-driven applications.

## Reference Resources

- **Official Documentation**: [https://tortoise.github.io/](https://tortoise.github.io/)
- **GitHub Repository**: [https://github.com/tortoise/tortoise-orm](https://github.com/tortoise/tortoise-orm)
- **Aerich Migration Tool**: [https://github.com/tortoise/aerich](https://github.com/tortoise/aerich)
- **Unfazed Command System**: [command.md#aerich](../features/command.md#aerich)
