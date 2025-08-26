Unfazed Admin 管理后台
======================

Unfazed Admin 是一个强大的 Web 管理后台系统，为 Unfazed 应用提供了完整的数据管理、用户权限控制和操作日志记录功能。它基于 Tortoise ORM 和 Unfazed Serializer 构建，提供了类似 Django Admin 的管理界面，但专为异步 Web 应用优化。

Unfazed Admin 模块只提供后端接口，前端需要使用 unfazed-admin 组件来构建管理后台。

## 系统概述

### 核心特性

- **模型管理**: 自动生成基于 Tortoise ORM 模型的 CRUD 操作界面
- **权限控制**: 基于用户角色的精细化权限管理系统
- **关系字段**: 支持外键、一对一、多对多关系的内联编辑
- **自定义操作**: 支持自定义业务操作和批量操作
- **操作日志**: 完整的操作记录和审计追踪
- **可扩展性**: 支持自定义字段、表单和页面组件

### 核心组件

- **AdminModelService**: 核心服务类，处理所有管理操作
- **ModelAdmin**: 模型管理器，定义模型的管理行为
- **CustomAdmin**: 自定义管理器，用于自定义管理界面
- **AdminCollector**: 管理器注册中心
- **LogEntry**: 操作日志模型
- **权限装饰器**: 基于角色的权限控制

## 快速开始

### 基本配置

```python
# settings.py
UNFAZED_SETTINGS = {
    "INSTALLED_APPS": [
        "unfazed.contrib.auth",
        "unfazed.contrib.admin",  # 启用 Admin 系统
        "myapp.users",
        "myapp.products",
    ],
    # 其他配置...
}
```

### 注册模型到 Admin

#### 与 Django Admin 的重要区别

**Django Admin** 直接注册 Model：
```python
# Django 方式
from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
```

**Unfazed Admin** 注册 Serializer：
```python
# Unfazed 方式
from unfazed.contrib.admin.registry import ModelAdmin, register
from unfazed.serializer import Serializer
from .models import User

class UserSerializer(Serializer):
    class Meta:
        model = User

@register(UserSerializer)  # 注册的是 Serializer，不是 Model
class UserAdmin(ModelAdmin):
    pass
```

#### 为什么使用 Serializer 而不是 Model？

**1. 更高的灵活性**
```python
class ProductSerializer(Serializer):
    # 自定义字段 - Model 中不存在的计算字段
    total_sales = fields.IntField(description="总销量")
    profit_margin = fields.FloatField(description="利润率")
    
    class Meta:
        model = Product
        # 精确控制显示的字段
        include = ["id", "name", "price", "category", "created_at"]
        # 或排除敏感字段
        exclude = ["internal_notes", "cost_price"]
    
    async def get_total_sales(self, obj):
        """计算总销量"""
        return await obj.order_items.all().count()
    
    async def get_profit_margin(self, obj):
        """计算利润率"""
        if obj.cost_price > 0:
            return ((obj.price - obj.cost_price) / obj.cost_price) * 100
        return 0
```

**2. 数据转换和格式化**
```python
class UserSerializer(Serializer):
    # 格式化显示
    full_name = fields.CharField(description="完整姓名")
    account_age = fields.IntField(description="账户年龄（天）")
    
    class Meta:
        model = User
        include = ["id", "username", "email", "is_active", "created_at"]
    
    async def get_full_name(self, obj):
        """组合显示完整姓名"""
        return f"{obj.first_name} {obj.last_name}".strip()
    
    async def get_account_age(self, obj):
        """计算账户年龄"""
        from datetime import datetime
        return (datetime.now() - obj.created_at).days
```

**3. 关系字段的精确控制**
```python
class OrderSerializer(Serializer):
    # 自定义关系字段显示
    customer_info = fields.DictField(description="客户信息")
    items_summary = fields.ListField(description="订单项摘要")
    
    class Meta:
        model = Order
        include = ["id", "order_number", "status", "total_amount", "created_at"]
        # 启用关系字段
        enable_relations = True
    
    async def get_customer_info(self, obj):
        """自定义客户信息显示"""
        return {
            "name": obj.customer.name,
            "email": obj.customer.email,
            "phone": obj.customer.phone,
            "vip_level": obj.customer.vip_level
        }
    
    async def get_items_summary(self, obj):
        """订单项摘要"""
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

**4. 业务逻辑封装**
```python
class ProductSerializer(Serializer):
    class Meta:
        model = Product
    
    # Serializer 提供的 CRUD 方法
    async def create_from_ctx(self, data):
        """自定义创建逻辑"""
        # 创建前的业务处理
        if data.get('category_id'):
            category = await Category.get(id=data['category_id'])
            if not category.is_active:
                raise ValueError("无法在非激活分类下创建产品")
        
        # 自动生成 SKU
        if not data.get('sku'):
            data['sku'] = await self.generate_sku(data)
        
        return await super().create_from_ctx(data)
    
    async def update_from_ctx(self, instance, data):
        """自定义更新逻辑"""
        # 价格变更记录
        if 'price' in data and data['price'] != instance.price:
            await PriceHistory.create(
                product=instance,
                old_price=instance.price,
                new_price=data['price'],
                changed_by=self.context.get('user')
            )
        
        return await super().update_from_ctx(instance, data)
    
    async def generate_sku(self, data):
        """生成产品 SKU"""
        category_code = await Category.get(id=data['category_id']).code
        count = await Product.all().count()
        return f"{category_code}{count + 1:06d}"
```

#### 完整示例

```python
# myapp/admin.py
from unfazed.contrib.admin.registry import ModelAdmin, register
from unfazed.serializer import Serializer
from .models import User, Product, Category

# 定义 Serializer
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

# 注册到 Admin
@register(UserSerializer)
class UserAdmin(ModelAdmin):
    # 基本配置
    route_label = "用户管理"
    help_text = "管理系统用户"
    
    # 界面配置
    icon = "user"
    component = "UserManagement"
    
    # 权限控制（可选重写）
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
    route_label = "产品管理"
    help_text = "管理产品信息"
    icon = "product"

@register(CategorySerializer)
class CategoryAdmin(ModelAdmin):
    route_label = "分类管理"
    help_text = "管理产品分类"
    icon = "category"
```

### 配置路由

```python
# urls.py
from unfazed.route import path, include

urlpatterns = [
    # Admin API 路由
    path("/api/contrib/admin/", include("unfazed.contrib.admin.routes")),
    # 其他路由...
]
```

## 模型管理详解

### ModelAdmin 配置

```python
from unfazed.contrib.admin.registry import ModelAdmin, register, action
from unfazed.contrib.admin.registry.schema import ActionKwargs
from unfazed.http import HttpResponse
import csv
import io

@register(ProductSerializer)
class ProductAdmin(ModelAdmin):
    # 基础配置
    route_label = "产品管理"
    help_text = "管理所有产品信息"
    
    # 界面配置
    icon = "shopping-cart"
    component = "ProductManagement"
    hideInMenu = False
    hideChildrenInMenu = False
    
    # 覆盖现有注册（如果存在同名 Admin）
    override = False
    
    # 权限控制
    async def has_view_perm(self, request) -> bool:
        """查看权限"""
        return request.user.is_authenticated
    
    async def has_create_perm(self, request) -> bool:
        """创建权限"""
        return request.user.is_superuser
    
    async def has_change_perm(self, request) -> bool:
        """修改权限"""
        return request.user.is_superuser
    
    async def has_delete_perm(self, request) -> bool:
        """删除权限"""
        return request.user.is_superuser
    
    async def has_action_perm(self, request) -> bool:
        """执行操作权限"""
        return request.user.is_superuser
    
    # 自定义操作
    @action(name="导出CSV", confirm=True)
    async def export_csv(self, ctx: ActionKwargs) -> HttpResponse:
        """导出产品数据为 CSV 文件"""
        # 获取查询条件
        queryset = ProductSerializer.get_queryset(ctx.search_condition)
        products = await ProductSerializer.list_from_ctx(queryset)
        
        # 生成 CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', '名称', '价格', '分类', '创建时间'])
        
        for product in products.data:
            writer.writerow([
                product['id'],
                product['name'],
                product['price'],
                product['category']['name'] if product.get('category') else '',
                product['created_at']
            ])
        
        # 返回 CSV 响应
        content = output.getvalue().encode('utf-8-sig')
        return HttpResponse(
            content,
            headers={
                'Content-Type': 'text/csv; charset=utf-8',
                'Content-Disposition': 'attachment; filename="products.csv"'
            }
        )
    
    @action(name="批量更新价格")
    async def bulk_update_price(self, ctx: ActionKwargs) -> dict:
        """批量更新产品价格"""
        factor = ctx.form_data.get('factor', 1.0)
        
        # 根据搜索条件获取产品
        queryset = ProductSerializer.get_queryset(ctx.search_condition)
        products = await queryset
        
        updated_count = 0
        for product in products:
            product.price = product.price * factor
            await product.save()
            updated_count += 1
        
        return {
            "message": f"成功更新 {updated_count} 个产品的价格",
            "updated_count": updated_count
        }
```

### 关系字段管理

```python
from unfazed.contrib.admin.registry import (
    ModelAdmin, ModelInlineAdmin, register,
    AdminRelation, AdminThrough
)

# 模型定义（示例）
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

# Admin 配置
@register(UserSerializer)
class UserAdmin(ModelAdmin):
    route_label = "用户管理"
    
    # 配置内联关系
    inlines = [
        # 一对一关系：用户档案
        AdminRelation(
            target="ProfileAdmin",
            source_field="id",
            target_field="user_id",
            relation="o2o"
        ),
        
        # 一对多关系：用户的书籍
        AdminRelation(
            target="BookAdmin",
            source_field="id", 
            target_field="author_id",
            relation="fk"
        ),
        
        # 多对多关系：用户角色（通过中间表）
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
    """内联管理器 - 用于在其他模型中嵌入管理"""
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

## 自定义操作按钮

### Action 装饰器

```python
from unfazed.contrib.admin.registry import action
from unfazed.contrib.admin.registry.schema import ActionKwargs
from unfazed.http import HttpResponse, JsonResponse
import json

@register(OrderSerializer)
class OrderAdmin(ModelAdmin):
    
    @action(name="确认订单", confirm=True)
    async def confirm_order(self, ctx: ActionKwargs) -> dict:
        """确认选中的订单"""
        # ctx.search_condition 包含筛选条件
        # ctx.form_data 包含表单数据
        # ctx.input_data 包含输入数据
        # ctx.request 包含当前请求对象
        
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
            "message": f"成功确认 {confirmed_count} 个订单",
            "confirmed_count": confirmed_count
        }
    
    @action(name="生成报表")
    async def generate_report(self, ctx: ActionKwargs) -> HttpResponse:
        """生成订单报表"""
        # 生成 Excel 报表
        import openpyxl
        from io import BytesIO
        
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "订单报表"
        
        # 表头
        headers = ['订单ID', '客户', '金额', '状态', '创建时间']
        for col, header in enumerate(headers, 1):
            ws.cell(row=1, column=col, value=header)
        
        # 数据
        queryset = OrderSerializer.get_queryset(ctx.search_condition)
        orders = await OrderSerializer.list_from_ctx(queryset)
        
        for row, order in enumerate(orders.data, 2):
            ws.cell(row=row, column=1, value=order['id'])
            ws.cell(row=row, column=2, value=order['customer']['name'])
            ws.cell(row=row, column=3, value=order['total_amount'])
            ws.cell(row=row, column=4, value=order['status'])
            ws.cell(row=row, column=5, value=order['created_at'])
        
        # 保存到内存
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
    
    @action(name="发送通知", confirm=False)
    async def send_notification(self, ctx: ActionKwargs) -> JsonResponse:
        """发送通知到选中的客户"""
        message = ctx.form_data.get('message', '')
        if not message:
            return JsonResponse({
                "success": False,
                "error": "请输入通知消息"
            }, status_code=400)
        
        queryset = OrderSerializer.get_queryset(ctx.search_condition)
        orders = await queryset
        
        # 获取唯一客户列表
        customers = set()
        for order in orders:
            customers.add(order.customer_id)
        
        # 发送通知（示例）
        sent_count = 0
        for customer_id in customers:
            # 这里集成实际的通知服务
            # await notification_service.send(customer_id, message)
            sent_count += 1
        
        return JsonResponse({
            "success": True,
            "message": f"成功发送通知给 {sent_count} 位客户",
            "sent_count": sent_count
        })
```

## 权限管理系统

### 基础权限控制

```python
from unfazed.contrib.admin.registry import ModelAdmin
from unfazed.http import HttpRequest

class SecureAdmin(ModelAdmin):
    """安全的 Admin 基类"""
    
    async def has_view_perm(self, request: HttpRequest) -> bool:
        """查看权限 - 需要登录"""
        return request.user.is_authenticated
    
    async def has_create_perm(self, request: HttpRequest) -> bool:
        """创建权限 - 需要员工权限"""
        return request.user.is_superuser
    
    async def has_change_perm(self, request: HttpRequest) -> bool:
        """修改权限 - 需要员工权限"""
        return request.user.is_superuser
    
    async def has_delete_perm(self, request: HttpRequest) -> bool:
        """删除权限 - 需要超级用户权限"""
        return request.user.is_superuser
    
    async def has_action_perm(self, request: HttpRequest) -> bool:
        """操作权限 - 需要员工权限"""
        return request.user.is_superuser

@register(ProductSerializer)
class ProductAdmin(SecureAdmin):
    route_label = "产品管理"
    
    # 可以进一步细化权限
    async def has_delete_perm(self, request: HttpRequest) -> bool:
        """产品删除需要特殊权限"""
        # 只有产品管理员或超级用户可以删除产品
        return (
            request.user.is_superuser or 
            await request.user.roles.filter(name="产品管理员").exists()
        )
```

### 基于角色的权限控制

```python
class RoleBasedAdmin(ModelAdmin):
    """基于角色的权限控制"""
    
    # 定义需要的角色
    view_roles = ["员工", "管理员", "超级管理员"]
    create_roles = ["管理员", "超级管理员"]
    change_roles = ["管理员", "超级管理员"]
    delete_roles = ["超级管理员"]
    action_roles = ["管理员", "超级管理员"]
    
    async def _has_role(self, request: HttpRequest, required_roles: list) -> bool:
        """检查用户是否具有所需角色"""
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
    route_label = "订单管理"
    
    # 订单管理需要特殊权限
    view_roles = ["销售员", "订单管理员", "财务", "管理员"]
    create_roles = ["销售员", "订单管理员", "管理员"]
    change_roles = ["订单管理员", "管理员"]
    delete_roles = ["管理员"]  # 只有管理员可以删除订单
```

## 操作日志系统

### LogEntry 模型

Admin 系统自动记录所有管理操作的日志：

```python
# unfazed/contrib/admin/models.py
class LogEntry(Model):
    id = fields.IntField(primary_key=True)
    created_at = fields.BigIntField()  # 时间戳
    account = fields.CharField(max_length=255)  # 操作用户
    path = fields.CharField(max_length=255)  # 请求路径
    ip = fields.CharField(max_length=128)  # 客户端IP
    request = fields.TextField()  # 请求数据
    response = fields.TextField()  # 响应数据
    
    class Meta:
        table = "unfazed_admin_logentry"
        indexes = ("account",)
```

### 日志装饰器

```python
# 自动记录日志的装饰器
from unfazed.contrib.admin.decorators import record

@login_required
@record  # 自动记录操作日志
async def model_save(request, ctx):
    # 保存操作会被自动记录
    pass

@login_required
@record  # 自动记录操作日志
async def model_delete(request, ctx):
    # 删除操作会被自动记录
    pass
```

### 查看操作日志

```python
@register(LogEntrySerializer)
class LogEntryAdmin(ModelAdmin):
    route_label = "操作日志"
    help_text = "查看系统操作记录"
    icon = "history"
    
    # 日志只允许查看，不允许修改
    async def has_create_perm(self, request) -> bool:
        return False
    
    async def has_change_perm(self, request) -> bool:
        return False
    
    async def has_delete_perm(self, request) -> bool:
        return request.user.is_superuser  # 只有超级用户可以删除日志
    
    # 自定义操作：清理旧日志
    @action(name="清理30天前日志", confirm=True)
    async def cleanup_old_logs(self, ctx: ActionKwargs) -> dict:
        """清理30天前的日志"""
        thirty_days_ago = int(time.time()) - (30 * 24 * 60 * 60)
        deleted_count = await LogEntry.filter(
            created_at__lt=thirty_days_ago
        ).count()
        
        await LogEntry.filter(created_at__lt=thirty_days_ago).delete()
        
        return {
            "success": True,
            "message": f"成功清理 {deleted_count} 条旧日志记录"
        }
```

## API 接口详解

### 核心 API 端点

Admin 系统提供以下 RESTful API 端点：

```python
# 路由列表 - 获取可访问的管理模块
GET /api/contrib/admin/route-list
# 响应: { "data": [AdminRoute] }

# 站点设置 - 获取管理站点配置
GET /api/contrib/admin/settings  
# 响应: { "data": AdminSite }

# 模型描述 - 获取模型字段定义
POST /api/contrib/admin/model-desc
# 请求: { "name": "UserAdmin" }
# 响应: { "data": AdminSerializeModel }

# 内联关系 - 获取模型关系字段
POST /api/contrib/admin/model-inlines
# 请求: { "name": "UserAdmin", "data": {} }
# 响应: { "data": { "ProfileAdmin": AdminInlineSerializeModel } }

# 模型数据 - 分页查询模型数据
POST /api/contrib/admin/model-data
# 请求: { "name": "UserAdmin", "cond": [], "page": 1, "size": 20 }
# 响应: { "data": { "data": [], "total": 0, "page": 1, "size": 20 } }

# 模型保存 - 创建或更新模型
POST /api/contrib/admin/model-save
# 请求: { "name": "UserAdmin", "data": { "id": 0, "name": "新用户" } }
# 响应: { "data": {...} }

# 模型删除 - 删除模型记录
POST /api/contrib/admin/model-delete
# 请求: { "name": "UserAdmin", "data": { "id": 1 } }
# 响应: { "data": {} }

# 模型操作 - 执行自定义操作
POST /api/contrib/admin/model-action
# 请求: { "name": "UserAdmin", "action": "export_csv", "search_condition": [], "form_data": {}, "input_data": {} }
# 响应: 取决于操作实现
```

### 查询条件格式

```python
# 条件查询格式
conditions = [
    {"field": "name", "eq": "张三"},           # 等于
    {"field": "age", "gt": 18},               # 大于
    {"field": "age", "gte": 18},              # 大于等于
    {"field": "age", "lt": 60},               # 小于
    {"field": "age", "lte": 60},              # 小于等于
    {"field": "status", "in": ["active", "pending"]},  # 包含
    {"field": "email", "like": "%@gmail.com"},  # 模糊匹配
    {"field": "deleted_at", "is_null": True},    # 空值
]
```


## 总结

Unfazed Admin 为现代异步 Web 应用提供了完整的后台管理解决方案：

**核心优势**：
- 🚀 **异步优化**: 基于 asyncio 的高性能异步操作
- 🎯 **易于使用**: 类似 Django Admin 的简洁 API
- 🔧 **功能完整**: CRUD、权限、日志、关系管理等全功能支持
- 📊 **灵活扩展**: 自定义操作、字段、权限控制
- 🛡️ **安全可靠**: 完整的权限系统和操作审计

**关键特性**：
- 自动化的模型管理界面生成
- 基于角色的细粒度权限控制
- 支持复杂关系字段的内联编辑
- 自定义业务操作和批量操作
- 完整的操作日志和审计追踪
- 高度可定制的字段和表单

通过 Unfazed Admin，开发者可以快速构建功能强大、安全可靠的管理后台，专注于业务逻辑的实现，而无需从零开始构建管理界面。

**技术亮点**：
- 📈 **高性能**: 异步数据库操作和查询优化
- 🎨 **设计优雅**: 清晰的架构和简洁的 API
- 🔄 **灵活配置**: 支持各种定制需求
- 🏆 **生产就绪**: 完整的安全机制和错误处理

无论是简单的内容管理还是复杂的企业级管理系统，Unfazed Admin 都能提供稳定、高效的解决方案。
