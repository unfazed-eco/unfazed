Unfazed 错误处理系统
===============

Unfazed 采用了独特的错误处理理念，倡导"异常优先"的开发模式。与传统框架不同，Unfazed 鼓励开发者在业务逻辑中专注于正常流程，将异常处理交由框架统一管理，从而简化代码逻辑并提高开发效率。

## 核心理念

### 异常优先设计
- **简化业务逻辑**: 开发者只需关注正常业务流程，无需到处使用 `try...except`
- **统一错误处理**: 框架提供标准化的错误响应格式
- **主动异常抛出**: 推荐使用异常而非 `if...else` 处理错误情况
- **调试友好**: 开发模式下提供详细的错误信息和调试界面

### 错误处理层次

1. **框架级异常**: 系统初始化、路由解析等框架层面的错误
2. **业务级异常**: 认证、权限、参数验证等业务逻辑错误
3. **应用级异常**: 用户自定义的业务异常
4. **系统级异常**: 数据库连接、文件操作等系统资源错误

## 快速开始

### 1. 配置错误处理中间件

在设置中启用 CommonMiddleware 来处理全局异常：

```python
# settings.py
UNFAZED_SETTINGS = {
    "MIDDLEWARES": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
    "DEBUG": True,  # 开发模式，生产环境请设为 False
}
```

> 在实际的业务开发中，建议自行实现 `CommonMiddleware` 来处理全局异常，并根据业务需求进行自定义。


### 2. 编写简洁的业务逻辑

专注于正常流程，让框架处理异常：

```python
import os
from unfazed.http import HttpRequest, JsonResponse

async def get_file_info(request: HttpRequest, file_path: str) -> JsonResponse:
    """获取文件信息 - 专注正常流程"""
    file_size = os.path.getsize(file_path)  # 框架会自动处理文件不存在的异常
    file_stat = os.stat(file_path)
    
    return JsonResponse({
        "file_path": file_path,
        "size": file_size,
        "modified_time": file_stat.st_mtime,
        "is_file": os.path.isfile(file_path)
    })
```

### 3. 主动抛出业务异常

使用异常来处理业务逻辑分支：

```python
from unfazed.exception import ParameterError

async def validate_and_get_file_info(request: HttpRequest, file_path: str) -> JsonResponse:
    """验证文件并获取信息"""
    
    # 主动验证和抛出异常，而非使用 if...else
    if not file_path.strip():
        raise ParameterError("文件路径不能为空")
    
    if not file_path.startswith('/safe/'):
        raise ParameterError("只允许访问 /safe/ 目录下的文件")
    
    try:
        file_size = os.path.getsize(file_path)
        return JsonResponse({
            "file_path": file_path,
            "size": file_size,
            "status": "success"
        })
    except FileNotFoundError:
        raise ParameterError(f"文件不存在: {file_path}")
    except PermissionError:
        raise ParameterError(f"没有权限访问文件: {file_path}")
```

## 内置异常类型

Unfazed 提供了丰富的内置异常类型，涵盖常见的业务场景：

### 基础异常类

Unfazed 不推荐使用 Restful 风格的状态码处理业务逻辑，而推荐在响应体中返回一个 `code` 字段来表示错误码，并根据错误码来判断错误类型。

```python
from unfazed.exception import BaseUnfazedException

class BaseUnfazedException(Exception):
    """Unfazed 异常基类"""
    def __init__(self, message: str, code: int = -1):
        self.message = message  # 错误消息
        self.code = code        # 错误代码
        super().__init__(message)
```

### HTTP 相关异常

```python
from unfazed.exception import MethodNotAllowed

# HTTP 方法不允许 (405)
raise MethodNotAllowed("该接口不支持 POST 方法")
```

### 参数验证异常

```python
from unfazed.exception import ParameterError

# 参数错误 (422)
raise ParameterError("用户ID必须是正整数")
raise ParameterError("邮箱格式不正确", code=1001)  # 自定义错误代码
```

### 认证授权异常

```python
from unfazed.exception import (
    LoginRequired,
    PermissionDenied,
    AccountNotFound,
    WrongPassword,
    AccountExisted
)

# 需要登录 (401)
raise LoginRequired("请先登录后再访问此资源")

# 权限不足 (403)
raise PermissionDenied("您没有权限执行此操作")

# 账户不存在 (404)
raise AccountNotFound("用户名或邮箱不存在")

# 密码错误 (405)
raise WrongPassword("密码不正确，请重试")

# 账户已存在 (406)
raise AccountExisted("该邮箱已被注册")
```

### 系统异常

```python
from unfazed.exception import UnfazedSetupError

# 框架初始化错误
raise UnfazedSetupError("数据库配置无效")
```

## 自定义异常

### 创建业务异常

继承 `BaseUnfazedException` 创建自定义业务异常：

```python
from unfazed.exception import BaseUnfazedException

class BusinessException(BaseUnfazedException):
    """业务异常基类"""
    pass

class InsufficientBalanceError(BusinessException):
    """余额不足异常"""
    def __init__(self, current_balance: float, required_amount: float):
        message = f"余额不足：当前余额 {current_balance}，需要 {required_amount}"
        super().__init__(message, code=2001)
        self.current_balance = current_balance
        self.required_amount = required_amount

class ProductOutOfStockError(BusinessException):
    """商品库存不足异常"""
    def __init__(self, product_id: str, available_stock: int):
        message = f"商品 {product_id} 库存不足，当前库存：{available_stock}"
        super().__init__(message, code=2002)
        self.product_id = product_id
        self.available_stock = available_stock

class InvalidDiscountCodeError(BusinessException):
    """无效优惠码异常"""
    def __init__(self, discount_code: str, reason: str = "优惠码无效"):
        message = f"优惠码 {discount_code} {reason}"
        super().__init__(message, code=2003)
        self.discount_code = discount_code
```

### 使用自定义异常

```python
from decimal import Decimal

async def process_payment(
    request: HttpRequest,
    user_id: int,
    amount: Decimal,
    discount_code: str = None
) -> JsonResponse:
    """处理支付请求"""
    
    # 获取用户余额
    user_balance = await get_user_balance(user_id)
    
    # 处理优惠码
    final_amount = amount
    if discount_code:
        try:
            discount = await validate_discount_code(discount_code, user_id)
            final_amount = amount * (1 - discount.percentage)
        except ValueError:
            raise InvalidDiscountCodeError(discount_code, "已过期或无效")
    
    # 检查余额
    if user_balance < final_amount:
        raise InsufficientBalanceError(float(user_balance), float(final_amount))
    
    # 处理支付
    payment_id = await process_payment_transaction(user_id, final_amount)
    
    return JsonResponse({
        "payment_id": payment_id,
        "amount": float(final_amount),
        "status": "success"
    })
```

## 错误处理中间件详解

### CommonMiddleware 工作原理

CommonMiddleware 是 Unfazed 的核心错误处理中间件，它的工作流程如下：

1. **异常捕获**: 拦截所有未处理的异常
2. **调试模式判断**: 根据 `DEBUG` 设置决定响应格式
3. **错误日志记录**: 自动记录错误详情到日志
4. **响应生成**: 生成标准化的错误响应

### 开发模式 vs 生产模式

#### 开发模式 (DEBUG=True)

开发模式下会显示详细的错误调试页面：

```python
# settings.py
UNFAZED_SETTINGS = {
    "DEBUG": True,
    "MIDDLEWARES": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
}
```

**调试页面包含**：
- 完整的错误堆栈信息
- 当前的 Unfazed 配置
- 美观的 HTML 错误页面
- 错误发生的详细上下文

#### 生产模式 (DEBUG=False)

生产模式下返回简洁的错误信息：

```python
# settings.py
UNFAZED_SETTINGS = {
    "DEBUG": False,
    "MIDDLEWARES": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
}
```

**生产模式特点**：
- 隐藏敏感的调试信息
- 返回统一的 "Internal Server Error" 响应
- 详细错误信息仅记录到日志
- 保护系统安全

### 中间件配置选项

```python
from unfazed.middleware.internal.common import CommonMiddleware

class CustomErrorMiddleware(CommonMiddleware):
    """自定义错误处理中间件"""
    
    async def handle_exception(self, exception: Exception, scope, receive, send):
        """自定义异常处理逻辑"""
        
        # 记录特定类型的异常
        if isinstance(exception, BusinessException):
            logger.warning(f"业务异常: {exception.message}")
            response = JsonResponse({
                "error": exception.message,
                "code": exception.code,
                "type": "business_error"
            }, status_code=400)
            
        elif isinstance(exception, BaseUnfazedException):
            logger.error(f"系统异常: {exception.message}")
            response = JsonResponse({
                "error": exception.message,
                "code": exception.code,
                "type": "system_error"
            }, status_code=500)
            
        else:
            # 未知异常
            logger.error(f"未知异常: {str(exception)}")
            response = JsonResponse({
                "error": "服务器内部错误",
                "code": -1,
                "type": "unknown_error"
            }, status_code=500)
        
        await response(scope, receive, send)
```

## 实际应用场景

### 用户认证场景

```python
from unfazed.exception import LoginRequired, PermissionDenied, AccountNotFound

async def get_user_profile(request: HttpRequest, user_id: int) -> JsonResponse:
    """获取用户资料"""
    
    # 检查登录状态
    current_user = await get_current_user(request)
    if not current_user:
        raise LoginRequired("请先登录")
    
    # 检查权限（只能查看自己的资料或管理员）
    if current_user.id != user_id and not current_user.is_admin:
        raise PermissionDenied("您只能查看自己的资料")
    
    # 获取目标用户
    target_user = await User.get_or_none(id=user_id)
    if not target_user:
        raise AccountNotFound(f"用户 {user_id} 不存在")
    
    return JsonResponse({
        "user_id": target_user.id,
        "username": target_user.username,
        "email": target_user.email,
        "created_at": target_user.created_at.isoformat()
    })
```

### 数据验证场景

```python
from unfazed.exception import ParameterError

async def create_product(request: HttpRequest, product_data: ProductCreateRequest) -> JsonResponse:
    """创建商品"""
    
    # 验证商品名称唯一性
    existing_product = await Product.get_or_none(name=product_data.name)
    if existing_product:
        raise ParameterError(f"商品名称 '{product_data.name}' 已存在")
    
    # 验证价格合理性
    if product_data.price <= 0:
        raise ParameterError("商品价格必须大于 0")
    
    if product_data.price > 1000000:
        raise ParameterError("商品价格不能超过 1,000,000")
    
    # 验证分类存在性
    category = await Category.get_or_none(id=product_data.category_id)
    if not category:
        raise ParameterError(f"商品分类 {product_data.category_id} 不存在")
    
    # 创建商品
    product = await Product.create(**product_data.model_dump())
    
    return JsonResponse({
        "product_id": product.id,
        "message": "商品创建成功"
    })
```

### 文件操作场景

```python
import aiofiles
from unfazed.exception import ParameterError

async def upload_file(request: HttpRequest, file: UploadFile) -> JsonResponse:
    """文件上传"""
    
    # 验证文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    if file.content_type not in allowed_types:
        raise ParameterError(f"不支持的文件类型: {file.content_type}")
    
    # 验证文件大小（5MB 限制）
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise ParameterError("文件大小不能超过 5MB")
    
    # 验证文件名
    if not file.filename or len(file.filename) > 255:
        raise ParameterError("文件名无效或过长")
    
    # 生成安全的文件名
    safe_filename = generate_safe_filename(file.filename)
    file_path = f"/uploads/{safe_filename}"
    
    # 保存文件
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
    except OSError as e:
        raise ParameterError(f"文件保存失败: {str(e)}")
    
    return JsonResponse({
        "filename": safe_filename,
        "size": len(content),
        "url": f"/static/uploads/{safe_filename}",
        "message": "文件上传成功"
    })
```

