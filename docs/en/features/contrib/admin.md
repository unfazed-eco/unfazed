Unfazed Admin Management Backend
=================================

Unfazed Admin is a powerful web management backend system that provides complete data management, user permission control, and operation logging for Unfazed applications. It's built on Tortoise ORM and Unfazed Serializer, offering an admin interface similar to Django Admin but optimized for async web applications.

The Unfazed Admin module only provides backend interfaces - the frontend requires the unfazed-admin component to build the management backend.

## System Overview

### Core Features

- **Model Management**: Auto-generate CRUD operation interfaces based on Tortoise ORM models
- **Permission Control**: Fine-grained permission management system based on user roles
- **Relationship Fields**: Support inline editing for foreign key, one-to-one, and many-to-many relationships
- **Custom Actions**: Support custom business operations and batch operations
- **Operation Logging**: Complete operation records and audit trails
- **Extensibility**: Support custom fields, forms, and page components

### Core Components

- **AdminModelService**: Core service class handling all management operations
- **ModelAdmin**: Model manager defining model management behavior
- **CustomAdmin**: Custom manager for custom management interfaces
- **AdminCollector**: Manager registration center
- **LogEntry**: Operation log model
- **Permission Decorators**: Role-based permission control

## Quick Start

### Basic Configuration

```python
# settings.py
UNFAZED_SETTINGS = {
    "INSTALLED_APPS": [
        "unfazed.contrib.auth",
        "unfazed.contrib.admin",  # Enable Admin system
        "myapp.users",
        "myapp.products",
    ],
    # Other configurations...
}
```

### Register Models to Admin

#### Important Difference from Django Admin

**Django Admin** directly registers Models:
```python
# Django way
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
```

**Unfazed Admin** registers Serializers:
```python
# Unfazed way
from unfazed.contrib.admin.registry import ModelAdmin, register
from unfazed.serializer import Serializer
from .models import User

class UserSerializer(Serializer):
    class Meta:
        model = User

@register(UserSerializer)  # Register Serializer, not Model
class UserAdmin(ModelAdmin):
    pass
```

#### Why Use Serializers Instead of Models?

**1. Higher Flexibility**
```python
class ProductSerializer(Serializer):
    # Custom fields - computed fields not in Model
    total_sales = fields.IntField(description="Total sales")
    profit_margin = fields.FloatField(description="Profit margin")
    
    class Meta:
        model = Product
        # Precise control of displayed fields
        include = ["id", "name", "price", "category", "created_at"]
        # Or exclude sensitive fields
        exclude = ["internal_notes", "cost_price"]
    
    async def get_total_sales(self, obj):
        """Calculate total sales"""
        return await obj.order_items.all().count()
    
    async def get_profit_margin(self, obj):
        """Calculate profit margin"""
        if obj.cost_price > 0:
            return ((obj.price - obj.cost_price) / obj.cost_price) * 100
        return 0
```

**2. Data Transformation and Formatting**
```python
class UserSerializer(Serializer):
    # Formatted display
    full_name = fields.CharField(description="Full name")
    account_age = fields.IntField(description="Account age (days)")
    
    class Meta:
        model = User
        include = ["id", "username", "email", "is_active", "created_at"]
    
    async def get_full_name(self, obj):
        """Combine to display full name"""
        return f"{obj.first_name} {obj.last_name}".strip()
    
    async def get_account_age(self, obj):
        """Calculate account age"""
        from datetime import datetime
        return (datetime.now() - obj.created_at).days
```

**3. Precise Control of Relationship Fields**
```python
class OrderSerializer(Serializer):
    # Custom relationship field display
    customer_info = fields.DictField(description="Customer information")
    items_summary = fields.ListField(description="Order items summary")
    
    class Meta:
        model = Order
        include = ["id", "order_number", "status", "total_amount", "created_at"]
        # Enable relationship fields
        enable_relations = True
    
    async def get_customer_info(self, obj):
        """Custom customer information display"""
        return {
            "name": obj.customer.name,
            "email": obj.customer.email,
            "phone": obj.customer.phone,
            "vip_level": obj.customer.vip_level
        }
    
    async def get_items_summary(self, obj):
        """Order items summary"""
        items = await obj.items.all().select_related("product")
        return [
            {
                "product": item.product.name,
                "quantity": item.quantity,
                "price": item.price
            }
            for item in items
        ]
```

**4. Business Logic Encapsulation**
```python
class ProductSerializer(Serializer):
    class Meta:
        model = Product
    
    # CRUD methods provided by Serializer
    async def create_from_ctx(self, data):
        """Custom creation logic"""
        # Business processing before creation
        if data.get('category_id'):
            category = await Category.get(id=data['category_id'])
            if not category.is_active:
                raise ValueError("Cannot create product in inactive category")
        
        # Auto-generate SKU
        if not data.get('sku'):
            data['sku'] = await self.generate_sku(data)
        
        return await super().create_from_ctx(data)
    
    async def update_from_ctx(self, instance, data):
        """Custom update logic"""
        # Price change record
        if 'price' in data and data['price'] != instance.price:
            await PriceHistory.create(
                product=instance,
                old_price=instance.price,
                new_price=data['price'],
                changed_by=self.context.get('user')
            )
        
        return await super().update_from_ctx(instance, data)
    
    async def generate_sku(self, data):
        """Generate product SKU"""
        category_code = await Category.get(id=data['category_id']).code
        count = await Product.all().count()
        return f"{category_code}{count + 1:06d}"
```

#### Complete Example

```python
# myapp/admin.py
from unfazed.contrib.admin.registry import ModelAdmin, register
from unfazed.serializer import Serializer
from .models import User, Product, Category

# Define Serializers
class UserSerializer(Serializer):
    class Meta:
        model = User

class ProductSerializer(Serializer):
    class Meta:
        model = Product
        include = ["id", "name", "price", "category", "created_at"]

class CategorySerializer(Serializer):
    class Meta:
        model = Category

# Register to Admin
@register(UserSerializer)
class UserAdmin(ModelAdmin):
    # Basic configuration
    route_label = "User Management"
    help_text = "Manage system users"
    
    # Interface configuration
    icon = "user"
    component = "UserManagement"
    
    # Permission control (optional override)
    async def has_view_perm(self, request) -> bool:
        return request.user.is_superuser
    
    async def has_create_perm(self, request) -> bool:
        return request.user.is_superuser
    
    async def has_change_perm(self, request) -> bool:
        return request.user.is_superuser
    
    async def has_delete_perm(self, request) -> bool:
        return request.user.is_superuser

@register(ProductSerializer)
class ProductAdmin(ModelAdmin):
    route_label = "Product Management"
    help_text = "Manage product information"
    icon = "product"

@register(CategorySerializer)
class CategoryAdmin(ModelAdmin):
    route_label = "Category Management"
    help_text = "Manage product categories"
    icon = "category"
```

### Configure Routes

```python
# urls.py
from unfazed.route import path, include

urlpatterns = [
    # Admin API routes
    path("/api/contrib/admin/", include("unfazed.contrib.admin.routes")),
    # Other routes...
]
```

## Model Management Details

### ModelAdmin Configuration

```python
from unfazed.contrib.admin.registry import ModelAdmin, register, action
from unfazed.contrib.admin.registry.schema import ActionKwargs
from unfazed.http import HttpResponse
import csv
import io

@register(ProductSerializer)
class ProductAdmin(ModelAdmin):
    # Basic configuration
    route_label = "Product Management"
    help_text = "Manage all product information"
    
    # Interface configuration
    icon = "shopping-cart"
    component = "ProductManagement"
    hideInMenu = False
    hideChildrenInMenu = False
    
    # Override existing registration (if same-named Admin exists)
    override = False
    
    # Permission control
    async def has_view_perm(self, request) -> bool:
        """View permission"""
        return request.user.is_authenticated
    
    async def has_create_perm(self, request) -> bool:
        """Create permission"""
        return request.user.is_superuser
    
    async def has_change_perm(self, request) -> bool:
        """Modify permission"""
        return request.user.is_superuser
    
    async def has_delete_perm(self, request) -> bool:
        """Delete permission"""
        return request.user.is_superuser
    
    async def has_action_perm(self, request) -> bool:
        """Execute action permission"""
        return request.user.is_superuser
    
    # Custom actions
    @action(name="Export CSV", confirm=True)
    async def export_csv(self, ctx: ActionKwargs) -> HttpResponse:
        """Export product data as CSV file"""
        # Get query conditions
        queryset = ProductSerializer.get_queryset(ctx.search_condition)
        products = await ProductSerializer.list_from_ctx(queryset)
        
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Name', 'Price', 'Category', 'Created At'])
        
        for product in products.data:
            writer.writerow([
                product['id'],
                product['name'],
                product['price'],
                product['category']['name'] if product.get('category') else '',
                product['created_at']
            ])
        
        # Return CSV response
        content = output.getvalue().encode('utf-8-sig')
        return HttpResponse(
            content,
            headers={
                'Content-Type': 'text/csv; charset=utf-8',
                'Content-Disposition': 'attachment; filename="products.csv"'
            }
        )
    
    @action(name="Bulk Update Price")
    async def bulk_update_price(self, ctx: ActionKwargs) -> dict:
        """Bulk update product prices"""
        factor = ctx.form_data.get('factor', 1.0)
        
        # Get products based on search conditions
        queryset = ProductSerializer.get_queryset(ctx.search_condition)
        products = await queryset
        
        updated_count = 0
        for product in products:
            product.price = product.price * factor
            await product.save()
            updated_count += 1
        
        return {
            "message": f"Successfully updated prices of {updated_count} products",
            "updated_count": updated_count
        }
```

### Relationship Field Management

```python
from unfazed.contrib.admin.registry import (
    ModelAdmin, ModelInlineAdmin, register,
    AdminRelation, AdminThrough
)

# Model definitions (example)
class User(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=255)

class Profile(Model):
    id = fields.IntField(primary_key=True)
    user = fields.OneToOneField("models.User", related_name="profile")
    bio = fields.TextField()

class Role(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=50)

class UserRole(Model):
    id = fields.IntField(primary_key=True)
    user = fields.ForeignKeyField("models.User")
    role = fields.ForeignKeyField("models.Role")

class Book(Model):
    id = fields.IntField(primary_key=True)
    title = fields.CharField(max_length=200)
    author = fields.ForeignKeyField("models.User", related_name="books")

# Admin configuration
@register(UserSerializer)
class UserAdmin(ModelAdmin):
    route_label = "User Management"
    
    # Configure inline relationships
    inlines = [
        # One-to-one relationship: user profile
        AdminRelation(
            target="ProfileAdmin",
            source_field="id",
            target_field="user_id",
            relation="o2o"
        ),
        
        # One-to-many relationship: user's books
        AdminRelation(
            target="BookAdmin",
            source_field="id", 
            target_field="author_id",
            relation="fk"
        ),
        
        # Many-to-many relationship: user roles (through intermediate table)
        AdminRelation(
            target="RoleAdmin",
            relation="m2m",
            through=AdminThrough(
                through="UserRoleAdmin",
                source_field="id",
                source_to_through_field="user_id",
                target_field="id",
                target_to_through_field="role_id"
            )
        ),
    ]

@register(ProfileSerializer)
class ProfileAdmin(ModelInlineAdmin):
    """Inline manager - for embedding in other models"""
    pass

@register(RoleSerializer) 
class RoleAdmin(ModelInlineAdmin):
    pass

@register(UserRoleSerializer)
class UserRoleAdmin(ModelInlineAdmin):
    pass

@register(BookSerializer)
class BookAdmin(ModelInlineAdmin):
    pass
```

## Custom Action Buttons

### Action Decorator

```python
from unfazed.contrib.admin.registry import action
from unfazed.contrib.admin.registry.schema import ActionKwargs
from unfazed.http import HttpResponse, JsonResponse
import json

@register(OrderSerializer)
class OrderAdmin(ModelAdmin):
    
    @action(name="Confirm Order", confirm=True)
    async def confirm_order(self, ctx: ActionKwargs) -> dict:
        """Confirm selected orders"""
        # ctx.search_condition contains filter conditions
        # ctx.form_data contains form data
        # ctx.input_data contains input data
        # ctx.request contains current request object
        
        queryset = OrderSerializer.get_queryset(ctx.search_condition)
        orders = await queryset
        
        confirmed_count = 0
        for order in orders:
            if order.status == 'pending':
                order.status = 'confirmed'
                order.confirmed_at = datetime.now()
                await order.save()
                confirmed_count += 1
        
        return {
            "success": True,
            "message": f"Successfully confirmed {confirmed_count} orders",
            "confirmed_count": confirmed_count
        }
    
    @action(name="Generate Report")
    async def generate_report(self, ctx: ActionKwargs) -> HttpResponse:
        """Generate order report"""
        # Generate Excel report
        import openpyxl
        from io import BytesIO
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Order Report"
        
        # Headers
        headers = ['Order ID', 'Customer', 'Amount', 'Status', 'Created At']
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        
        # Data
        queryset = OrderSerializer.get_queryset(ctx.search_condition)
        orders = await OrderSerializer.list_from_ctx(queryset)
        
        for row, order in enumerate(orders.data, 2):
            ws.cell(row=row, column=1, value=order['id'])
            ws.cell(row=row, column=2, value=order['customer']['name'])
            ws.cell(row=row, column=3, value=order['total_amount'])
            ws.cell(row=row, column=4, value=order['status'])
            ws.cell(row=row, column=5, value=order['created_at'])
        
        # Save to memory
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        return HttpResponse(
            buffer.getvalue(),
            headers={
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'Content-Disposition': 'attachment; filename="order_report.xlsx"'
            }
        )
    
    @action(name="Send Notification", confirm=False)
    async def send_notification(self, ctx: ActionKwargs) -> JsonResponse:
        """Send notification to selected customers"""
        message = ctx.form_data.get('message', '')
        if not message:
            return JsonResponse({
                "success": False,
                "error": "Please enter notification message"
            }, status_code=400)
        
        queryset = OrderSerializer.get_queryset(ctx.search_condition)
        orders = await queryset
        
        # Get unique customer list
        customers = set()
        for order in orders:
            customers.add(order.customer_id)
        
        # Send notifications (example)
        sent_count = 0
        for customer_id in customers:
            # Integrate with actual notification service here
            # await notification_service.send(customer_id, message)
            sent_count += 1
        
        return JsonResponse({
            "success": True,
            "message": f"Successfully sent notifications to {sent_count} customers",
            "sent_count": sent_count
        })
```

## Permission Management System

### Basic Permission Control

```python
from unfazed.contrib.admin.registry import ModelAdmin
from unfazed.http import HttpRequest

class SecureAdmin(ModelAdmin):
    """Secure Admin base class"""
    
    async def has_view_perm(self, request: HttpRequest) -> bool:
        """View permission - requires login"""
        return request.user.is_authenticated
    
    async def has_create_perm(self, request: HttpRequest) -> bool:
        """Create permission - requires staff privileges"""
        return request.user.is_superuser
    
    async def has_change_perm(self, request: HttpRequest) -> bool:
        """Modify permission - requires staff privileges"""
        return request.user.is_superuser
    
    async def has_delete_perm(self, request: HttpRequest) -> bool:
        """Delete permission - requires superuser privileges"""
        return request.user.is_superuser
    
    async def has_action_perm(self, request: HttpRequest) -> bool:
        """Action permission - requires staff privileges"""
        return request.user.is_superuser

@register(ProductSerializer)
class ProductAdmin(SecureAdmin):
    route_label = "Product Management"
    
    # Can further refine permissions
    async def has_delete_perm(self, request: HttpRequest) -> bool:
        """Product deletion requires special permission"""
        # Only product administrators or superusers can delete products
        return (
            request.user.is_superuser or 
            await request.user.roles.filter(name="Product Administrator").exists()
        )
```

### Role-Based Permission Control

```python
class RoleBasedAdmin(ModelAdmin):
    """Role-based permission control"""
    
    # Define required roles
    view_roles = ["Staff", "Administrator", "Super Administrator"]
    create_roles = ["Administrator", "Super Administrator"]
    change_roles = ["Administrator", "Super Administrator"]
    delete_roles = ["Super Administrator"]
    action_roles = ["Administrator", "Super Administrator"]
    
    async def _has_role(self, request: HttpRequest, required_roles: list) -> bool:
        """Check if user has required roles"""
        if not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        user_roles = await request.user.roles.all().values_list("name", flat=True)
        return any(role in user_roles for role in required_roles)
    
    async def has_view_perm(self, request: HttpRequest) -> bool:
        return await self._has_role(request, self.view_roles)
    
    async def has_create_perm(self, request: HttpRequest) -> bool:
        return await self._has_role(request, self.create_roles)
    
    async def has_change_perm(self, request: HttpRequest) -> bool:
        return await self._has_role(request, self.change_roles)
    
    async def has_delete_perm(self, request: HttpRequest) -> bool:
        return await self._has_role(request, self.delete_roles)
    
    async def has_action_perm(self, request: HttpRequest) -> bool:
        return await self._has_role(request, self.action_roles)

@register(OrderSerializer)
class OrderAdmin(RoleBasedAdmin):
    route_label = "Order Management"
    
    # Order management requires special permissions
    view_roles = ["Sales", "Order Manager", "Finance", "Administrator"]
    create_roles = ["Sales", "Order Manager", "Administrator"]
    change_roles = ["Order Manager", "Administrator"]
    delete_roles = ["Administrator"]  # Only administrators can delete orders
```

## Operation Log System

### LogEntry Model

The Admin system automatically logs all management operations:

```python
# unfazed/contrib/admin/models.py
class LogEntry(Model):
    id = fields.IntField(primary_key=True)
    created_at = fields.BigIntField()  # Timestamp
    account = fields.CharField(max_length=255)  # Operating user
    path = fields.CharField(max_length=255)  # Request path
    ip = fields.CharField(max_length=128)  # Client IP
    request = fields.TextField()  # Request data
    response = fields.TextField()  # Response data
    
    class Meta:
        table = "unfazed_admin_logentry"
        indexes = ("account",)
```

### Log Decorator

```python
# Auto-logging decorator
from unfazed.contrib.admin.decorators import record

@login_required
@record  # Automatically record operation logs
async def model_save(request, ctx):
    # Save operations will be automatically logged
    pass

@login_required
@record  # Automatically record operation logs
async def model_delete(request, ctx):
    # Delete operations will be automatically logged
    pass
```

### View Operation Logs

```python
@register(LogEntrySerializer)
class LogEntryAdmin(ModelAdmin):
    route_label = "Operation Logs"
    help_text = "View system operation records"
    icon = "history"
    
    # Logs are read-only
    async def has_create_perm(self, request) -> bool:
        return False
    
    async def has_change_perm(self, request) -> bool:
        return False
    
    async def has_delete_perm(self, request) -> bool:
        return request.user.is_superuser  # Only superusers can delete logs
    
    # Custom action: clean old logs
    @action(name="Clean 30-day Old Logs", confirm=True)
    async def cleanup_old_logs(self, ctx: ActionKwargs) -> dict:
        """Clean logs older than 30 days"""
        thirty_days_ago = int(time.time()) - (30 * 24 * 60 * 60)
        deleted_count = await LogEntry.filter(
            created_at__lt=thirty_days_ago
        ).count()
        
        await LogEntry.filter(created_at__lt=thirty_days_ago).delete()
        
        return {
            "success": True,
            "message": f"Successfully cleaned {deleted_count} old log records"
        }
```

## API Interface Details

### Core API Endpoints

The Admin system provides the following RESTful API endpoints:

```python
# Route list - get accessible management modules
GET /api/contrib/admin/route-list
# Response: { "data": [AdminRoute] }

# Site settings - get management site configuration
GET /api/contrib/admin/settings  
# Response: { "data": AdminSite }

# Model description - get model field definitions
POST /api/contrib/admin/model-desc
# Request: { "name": "UserAdmin" }
# Response: { "data": AdminSerializeModel }

# Inline relationships - get model relationship fields
POST /api/contrib/admin/model-inlines
# Request: { "name": "UserAdmin", "data": {} }
# Response: { "data": { "ProfileAdmin": AdminInlineSerializeModel } }

# Model data - paginated query of model data
POST /api/contrib/admin/model-data
# Request: { "name": "UserAdmin", "cond": [], "page": 1, "size": 20 }
# Response: { "data": { "data": [], "total": 0, "page": 1, "size": 20 } }

# Model save - create or update model
POST /api/contrib/admin/model-save
# Request: { "name": "UserAdmin", "data": { "id": 0, "name": "New User" } }
# Response: { "data": {...} }

# Model delete - delete model record
POST /api/contrib/admin/model-delete
# Request: { "name": "UserAdmin", "data": { "id": 1 } }
# Response: { "data": {} }

# Model action - execute custom action
POST /api/contrib/admin/model-action
# Request: { "name": "UserAdmin", "action": "export_csv", "search_condition": [], "form_data": {}, "input_data": {} }
# Response: depends on action implementation
```

### Query Condition Format

```python
# Query condition format
conditions = [
    {"field": "name", "eq": "John"},           # equals
    {"field": "age", "gt": 18},               # greater than
    {"field": "age", "gte": 18},              # greater than or equal
    {"field": "age", "lt": 60},               # less than
    {"field": "age", "lte": 60},              # less than or equal
    {"field": "status", "in": ["active", "pending"]},  # contains
    {"field": "email", "like": "%@gmail.com"},  # fuzzy match
    {"field": "deleted_at", "is_null": True},    # null value
]
```

## Summary

Unfazed Admin provides a complete backend management solution for modern async web applications:

**Core Advantages**:
- 🚀 **Async Optimized**: High-performance async operations based on asyncio
- 🎯 **Easy to Use**: Simple API similar to Django Admin
- 🔧 **Full-Featured**: Complete CRUD, permissions, logging, relationship management support
- 📊 **Flexible Extension**: Custom actions, fields, permission control
- 🛡️ **Secure and Reliable**: Complete permission system and operation auditing

**Key Features**:
- Automated model management interface generation
- Role-based fine-grained permission control
- Support for complex relationship field inline editing
- Custom business actions and batch operations
- Complete operation logs and audit trails
- Highly customizable fields and forms

Through Unfazed Admin, developers can quickly build powerful, secure, and reliable management backends, focusing on business logic implementation without building management interfaces from scratch.

**Technical Highlights**:
- 📈 **High Performance**: Async database operations and query optimization
- 🎨 **Elegant Design**: Clear architecture and simple API
- 🔄 **Flexible Configuration**: Support for various customization needs
- 🏆 **Production Ready**: Complete security mechanisms and error handling

Whether for simple content management or complex enterprise-level management systems, Unfazed Admin provides stable and efficient solutions.
