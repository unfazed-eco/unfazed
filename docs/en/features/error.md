Unfazed Error Handling System
===============

Unfazed adopts a unique error handling philosophy, advocating an "exception-first" development mode. Unlike traditional frameworks, Unfazed encourages developers to focus on normal processes in business logic, leaving exception handling to be managed uniformly by the framework, thereby simplifying code logic and improving development efficiency.

## Core Philosophy

### Exception-First Design
- **Simplify Business Logic**: Developers only need to focus on normal business processes, no need to use `try...except` everywhere
- **Unified Error Handling**: Framework provides standardized error response formats
- **Proactive Exception Throwing**: Recommend using exceptions instead of `if...else` to handle error conditions
- **Debug Friendly**: Provides detailed error information and debug interface in development mode

### Error Handling Hierarchy

1. **Framework-level Exceptions**: System initialization, route parsing and other framework-level errors
2. **Business-level Exceptions**: Authentication, permissions, parameter validation and other business logic errors
3. **Application-level Exceptions**: User-defined business exceptions
4. **System-level Exceptions**: Database connections, file operations and other system resource errors

## Quick Start

### 1. Configure Error Handling Middleware

Enable CommonMiddleware in settings to handle global exceptions:

```python
# settings.py
UNFAZED_SETTINGS = {
    "MIDDLEWARES": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
    "DEBUG": True,  # Development mode, set to False in production
}
```

> In actual business development, it's recommended to implement your own `CommonMiddleware` to handle global exceptions and customize according to business needs.


### 2. Write Clean Business Logic

Focus on normal processes and let the framework handle exceptions:

```python
import os
from unfazed.http import HttpRequest, JsonResponse

async def get_file_info(request: HttpRequest, file_path: str) -> JsonResponse:
    """Get file information - focus on normal process"""
    file_size = os.path.getsize(file_path)  # Framework will automatically handle file not found exception
    file_stat = os.stat(file_path)
    
    return JsonResponse({
        "file_path": file_path,
        "size": file_size,
        "modified_time": file_stat.st_mtime,
        "is_file": os.path.isfile(file_path)
    })
```

### 3. Proactively Throw Business Exceptions

Use exceptions to handle business logic branches:

```python
from unfazed.exception import ParameterError

async def validate_and_get_file_info(request: HttpRequest, file_path: str) -> JsonResponse:
    """Validate file and get information"""
    
    # Proactively validate and throw exceptions, instead of using if...else
    if not file_path.strip():
        raise ParameterError("File path cannot be empty")
    
    if not file_path.startswith('/safe/'):
        raise ParameterError("Only files under /safe/ directory are allowed")
    
    try:
        file_size = os.path.getsize(file_path)
        return JsonResponse({
            "file_path": file_path,
            "size": file_size,
            "status": "success"
        })
    except FileNotFoundError:
        raise ParameterError(f"File not found: {file_path}")
    except PermissionError:
        raise ParameterError(f"No permission to access file: {file_path}")
```

## Built-in Exception Types

Unfazed provides rich built-in exception types covering common business scenarios:

### Base Exception Class

Unfazed doesn't recommend using RESTful style status codes to handle business logic, but recommends returning a `code` field in the response body to represent error codes, and judging error types based on error codes.

```python
from unfazed.exception import BaseUnfazedException

class BaseUnfazedException(Exception):
    """Unfazed exception base class"""
    def __init__(self, message: str, code: int = -1):
        self.message = message  # Error message
        self.code = code        # Error code
        super().__init__(message)
```

### HTTP Related Exceptions

```python
from unfazed.exception import MethodNotAllowed

# HTTP method not allowed (405)
raise MethodNotAllowed("This API does not support POST method")
```

### Parameter Validation Exceptions

```python
from unfazed.exception import ParameterError

# Parameter error (422)
raise ParameterError("User ID must be a positive integer")
raise ParameterError("Email format is incorrect", code=1001)  # Custom error code
```

### Authentication Authorization Exceptions

```python
from unfazed.exception import (
    LoginRequired,
    PermissionDenied,
    AccountNotFound,
    WrongPassword,
    AccountExisted
)

# Login required (401)
raise LoginRequired("Please log in before accessing this resource")

# Insufficient permissions (403)
raise PermissionDenied("You don't have permission to perform this operation")

# Account not found (404)
raise AccountNotFound("Username or email does not exist")

# Wrong password (405)
raise WrongPassword("Password is incorrect, please try again")

# Account already exists (406)
raise AccountExisted("This email has already been registered")
```

### System Exceptions

```python
from unfazed.exception import UnfazedSetupError

# Framework initialization error
raise UnfazedSetupError("Database configuration is invalid")
```

## Custom Exceptions

### Creating Business Exceptions

Inherit from `BaseUnfazedException` to create custom business exceptions:

```python
from unfazed.exception import BaseUnfazedException

class BusinessException(BaseUnfazedException):
    """Business exception base class"""
    pass

class InsufficientBalanceError(BusinessException):
    """Insufficient balance exception"""
    def __init__(self, current_balance: float, required_amount: float):
        message = f"Insufficient balance: current balance {current_balance}, required {required_amount}"
        super().__init__(message, code=2001)
        self.current_balance = current_balance
        self.required_amount = required_amount

class ProductOutOfStockError(BusinessException):
    """Product out of stock exception"""
    def __init__(self, product_id: str, available_stock: int):
        message = f"Product {product_id} out of stock, current stock: {available_stock}"
        super().__init__(message, code=2002)
        self.product_id = product_id
        self.available_stock = available_stock

class InvalidDiscountCodeError(BusinessException):
    """Invalid discount code exception"""
    def __init__(self, discount_code: str, reason: str = "Invalid discount code"):
        message = f"Discount code {discount_code} {reason}"
        super().__init__(message, code=2003)
        self.discount_code = discount_code
```

### Using Custom Exceptions

```python
from decimal import Decimal

async def process_payment(
    request: HttpRequest,
    user_id: int,
    amount: Decimal,
    discount_code: str = None
) -> JsonResponse:
    """Process payment request"""
    
    # Get user balance
    user_balance = await get_user_balance(user_id)
    
    # Process discount code
    final_amount = amount
    if discount_code:
        try:
            discount = await validate_discount_code(discount_code, user_id)
            final_amount = amount * (1 - discount.percentage)
        except ValueError:
            raise InvalidDiscountCodeError(discount_code, "expired or invalid")
    
    # Check balance
    if user_balance < final_amount:
        raise InsufficientBalanceError(float(user_balance), float(final_amount))
    
    # Process payment
    payment_id = await process_payment_transaction(user_id, final_amount)
    
    return JsonResponse({
        "payment_id": payment_id,
        "amount": float(final_amount),
        "status": "success"
    })
```

## Error Handling Middleware Details

### CommonMiddleware Working Principle

CommonMiddleware is Unfazed's core error handling middleware, its workflow is as follows:

1. **Exception Capture**: Intercept all unhandled exceptions
2. **Debug Mode Judgment**: Decide response format based on `DEBUG` setting
3. **Error Logging**: Automatically record error details to logs
4. **Response Generation**: Generate standardized error responses

### Development Mode vs Production Mode

#### Development Mode (DEBUG=True)

Development mode shows detailed error debug pages:

```python
# settings.py
UNFAZED_SETTINGS = {
    "DEBUG": True,
    "MIDDLEWARES": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
}
```

**Debug page includes**:
- Complete error stack information
- Current Unfazed configuration
- Beautiful HTML error pages
- Detailed context where error occurred

#### Production Mode (DEBUG=False)

Production mode returns concise error information:

```python
# settings.py
UNFAZED_SETTINGS = {
    "DEBUG": False,
    "MIDDLEWARES": [
        "unfazed.middleware.internal.common.CommonMiddleware",
    ],
}
```

**Production mode features**:
- Hide sensitive debug information
- Return unified "Internal Server Error" responses
- Detailed error information only recorded in logs
- Protect system security

### Middleware Configuration Options

```python
from unfazed.middleware.internal.common import CommonMiddleware

class CustomErrorMiddleware(CommonMiddleware):
    """Custom error handling middleware"""
    
    async def handle_exception(self, exception: Exception, scope, receive, send):
        """Custom exception handling logic"""
        
        # Record specific types of exceptions
        if isinstance(exception, BusinessException):
            logger.warning(f"Business exception: {exception.message}")
            response = JsonResponse({
                "error": exception.message,
                "code": exception.code,
                "type": "business_error"
            }, status_code=400)
            
        elif isinstance(exception, BaseUnfazedException):
            logger.error(f"System exception: {exception.message}")
            response = JsonResponse({
                "error": exception.message,
                "code": exception.code,
                "type": "system_error"
            }, status_code=500)
            
        else:
            # Unknown exception
            logger.error(f"Unknown exception: {str(exception)}")
            response = JsonResponse({
                "error": "Internal server error",
                "code": -1,
                "type": "unknown_error"
            }, status_code=500)
        
        await response(scope, receive, send)
```

## Practical Application Scenarios

### User Authentication Scenario

```python
from unfazed.exception import LoginRequired, PermissionDenied, AccountNotFound

async def get_user_profile(request: HttpRequest, user_id: int) -> JsonResponse:
    """Get user profile"""
    
    # Check login status
    current_user = await get_current_user(request)
    if not current_user:
        raise LoginRequired("Please log in first")
    
    # Check permissions (can only view own profile or admin)
    if current_user.id != user_id and not current_user.is_admin:
        raise PermissionDenied("You can only view your own profile")
    
    # Get target user
    target_user = await User.get_or_none(id=user_id)
    if not target_user:
        raise AccountNotFound(f"User {user_id} does not exist")
    
    return JsonResponse({
        "user_id": target_user.id,
        "username": target_user.username,
        "email": target_user.email,
        "created_at": target_user.created_at.isoformat()
    })
```

### Data Validation Scenario

```python
from unfazed.exception import ParameterError

async def create_product(request: HttpRequest, product_data: ProductCreateRequest) -> JsonResponse:
    """Create product"""
    
    # Validate product name uniqueness
    existing_product = await Product.get_or_none(name=product_data.name)
    if existing_product:
        raise ParameterError(f"Product name '{product_data.name}' already exists")
    
    # Validate price reasonableness
    if product_data.price <= 0:
        raise ParameterError("Product price must be greater than 0")
    
    if product_data.price > 1000000:
        raise ParameterError("Product price cannot exceed 1,000,000")
    
    # Validate category existence
    category = await Category.get_or_none(id=product_data.category_id)
    if not category:
        raise ParameterError(f"Product category {product_data.category_id} does not exist")
    
    # Create product
    product = await Product.create(**product_data.model_dump())
    
    return JsonResponse({
        "product_id": product.id,
        "message": "Product created successfully"
    })
```

### File Operation Scenario

```python
import aiofiles
from unfazed.exception import ParameterError

async def upload_file(request: HttpRequest, file: UploadFile) -> JsonResponse:
    """File upload"""
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif']
    if file.content_type not in allowed_types:
        raise ParameterError(f"Unsupported file type: {file.content_type}")
    
    # Validate file size (5MB limit)
    content = await file.read()
    if len(content) > 5 * 1024 * 1024:
        raise ParameterError("File size cannot exceed 5MB")
    
    # Validate filename
    if not file.filename or len(file.filename) > 255:
        raise ParameterError("Invalid or too long filename")
    
    # Generate safe filename
    safe_filename = generate_safe_filename(file.filename)
    file_path = f"/uploads/{safe_filename}"
    
    # Save file
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
    except OSError as e:
        raise ParameterError(f"File save failed: {str(e)}")
    
    return JsonResponse({
        "filename": safe_filename,
        "size": len(content),
        "url": f"/static/uploads/{safe_filename}",
        "message": "File uploaded successfully"
    })
```
