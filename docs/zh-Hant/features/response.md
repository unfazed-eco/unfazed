Unfazed HttpResponse
====

Unfazed 提供了一套完整的 HTTP 响应类系统，基于 Starlette 的响应类并进行了功能增强。所有的视图函数都必须返回 `HttpResponse` 类型的对象。

## 响应系统概述

### 核心特性

- **多种响应类型**: 支持文本、HTML、JSON、文件、流式响应等多种类型
- **高性能 JSON**: 使用 orjson 提供高性能的 JSON 序列化
- **文件断点续传**: 内置 HTTP Range 请求支持，实现断点下载
- **流式响应**: 支持异步流式数据传输，适合大文件和实时数据
- **自动头部处理**: 自动设置正确的 Content-Type 和其他必要头部
- **背景任务**: 支持响应发送后执行的背景任务

### 响应类型层次结构

```python
HttpResponse (基础响应类)
├── PlainTextResponse (纯文本响应)
├── HtmlResponse (HTML响应)
├── JsonResponse (JSON响应)
├── RedirectResponse (重定向响应)
├── StreamingResponse (流式响应)
└── FileResponse (文件响应，继承自StreamingResponse)
```

### 基础签名

```python
class HttpResponse[T]:
    def __init__(
        self,
        content: T | None = None,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None: ...
```

## 基本用法

### 简单示例

```python
from unfazed.http import HttpRequest, HttpResponse, JsonResponse
from starlette.background import BackgroundTask

async def simple_response(request: HttpRequest) -> HttpResponse:
    """最简单的响应"""
    return HttpResponse("Hello, World!")

async def with_status_and_headers(request: HttpRequest) -> HttpResponse:
    """带状态码和头部的响应"""
    return HttpResponse(
        content="自定义响应",
        status_code=201,
        headers={"X-Custom-Header": "MyValue"},
        media_type="text/plain; charset=utf-8"
    )

def cleanup_task():
    """背景任务示例"""
    print("响应发送后执行的清理任务")

async def with_background_task(request: HttpRequest) -> HttpResponse:
    """带背景任务的响应"""
    task = BackgroundTask(cleanup_task)
    return HttpResponse(
        content="任务已提交",
        background=task
    )
```

## 响应类型详解

### PlainTextResponse - 纯文本响应

用于返回纯文本内容，Content-Type 为 `text/plain`。

```python
from unfazed.http import PlainTextResponse

async def text_response(request: HttpRequest) -> PlainTextResponse:
    """返回纯文本"""
    return PlainTextResponse("这是纯文本响应")

async def text_with_encoding(request: HttpRequest) -> PlainTextResponse:
    """指定编码的文本响应"""
    return PlainTextResponse(
        content="带编码的文本响应",
        headers={"Content-Type": "text/plain; charset=utf-8"}
    )

async def multiline_text(request: HttpRequest) -> PlainTextResponse:
    """多行文本响应"""
    text_content = """
    这是多行文本响应
    第二行内容
    第三行内容
    """
    return PlainTextResponse(text_content.strip())
```

### HtmlResponse - HTML响应

用于返回 HTML 内容，Content-Type 为 `text/html`。

```python
from unfazed.http import HtmlResponse

async def html_page(request: HttpRequest) -> HtmlResponse:
    """返回HTML页面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Unfazed HTML响应</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>欢迎使用 Unfazed</h1>
        <p>这是一个HTML响应示例</p>
    </body>
    </html>
    """
    return HtmlResponse(html_content)

async def dynamic_html(request: HttpRequest) -> HtmlResponse:
    """动态HTML内容"""
    user_name = request.query_params.get("name", "访客")
    html_content = f"""
    <html>
    <body>
        <h1>Hello, {user_name}!</h1>
        <p>当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </body>
    </html>
    """
    return HtmlResponse(html_content)

async def error_page(request: HttpRequest) -> HtmlResponse:
    """错误页面"""
    error_html = """
    <html>
    <body style="font-family: Arial;">
        <h1 style="color: red;">404 - 页面未找到</h1>
        <p>抱歉，您访问的页面不存在。</p>
        <a href="/">返回首页</a>
    </body>
    </html>
    """
    return HtmlResponse(error_html, status_code=404)
```

### JsonResponse - JSON响应

用于返回 JSON 数据，支持字典、列表和 Pydantic 模型的自动序列化。

```python
from unfazed.http import JsonResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# 基本用法
async def json_dict(request: HttpRequest) -> JsonResponse:
    """返回字典"""
    return JsonResponse({"message": "Hello, World!", "status": "success"})

async def json_list(request: HttpRequest) -> JsonResponse:
    """返回列表"""
    return JsonResponse([1, 2, 3, {"name": "item"}])

# Pydantic 模型
class User(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True

class UserListResponse(BaseModel):
    users: List[User]
    total: int
    page: int
    size: int

async def json_model(request: HttpRequest) -> JsonResponse:
    """返回 Pydantic 模型"""
    user = User(
        id=1,
        username="john_doe",
        email="john@example.com"
    )
    return JsonResponse(user)

async def json_complex_model(request: HttpRequest) -> JsonResponse:
    """返回复杂模型"""
    users = [
        User(id=1, username="alice", email="alice@example.com"),
        User(id=2, username="bob", email="bob@example.com"),
    ]
    
    response = UserListResponse(
        users=users,
        total=len(users),
        page=1,
        size=10
    )
    return JsonResponse(response)

# 自定义状态码和头部
async def json_with_custom_headers(request: HttpRequest) -> JsonResponse:
    """带自定义头部的JSON响应"""
    data = {"message": "资源已创建", "id": 123}
    return JsonResponse(
        content=data,
        status_code=201,
        headers={
            "Location": "/api/resources/123",
            "X-Resource-ID": "123"
        }
    )

# 错误响应
async def json_error(request: HttpRequest) -> JsonResponse:
    """JSON错误响应"""
    error_data = {
        "error": "参数验证失败",
        "code": "VALIDATION_ERROR",
        "details": {
            "field": "email",
            "message": "邮箱格式不正确"
        }
    }
    return JsonResponse(error_data, status_code=400)
```

### RedirectResponse - 重定向响应

用于 HTTP 重定向，自动处理 URL 编码和安全验证。

```python
from unfazed.http import RedirectResponse

async def temporary_redirect(request: HttpRequest) -> RedirectResponse:
    """临时重定向 (302)"""
    return RedirectResponse("https://www.example.com")

async def permanent_redirect(request: HttpRequest) -> RedirectResponse:
    """永久重定向 (301)"""
    return RedirectResponse(
        "https://www.newdomain.com",
        status_code=301
    )

async def login_redirect(request: HttpRequest) -> RedirectResponse:
    """登录重定向"""
    # 检查用户是否已登录
    if not hasattr(request, 'user') or not request.user:
        # 重定向到登录页面，并保存原始URL
        original_url = str(request.url)
        login_url = f"https://auth.example.com/login?next={original_url}"
        return RedirectResponse(login_url)
    
    # 用户已登录，重定向到仪表板
    return RedirectResponse("https://app.example.com/dashboard")

async def conditional_redirect(request: HttpRequest) -> RedirectResponse:
    """条件重定向"""
    user_agent = request.headers.get("user-agent", "").lower()
    
    if "mobile" in user_agent:
        return RedirectResponse("https://m.example.com")
    else:
        return RedirectResponse("https://www.example.com")
```

**注意**: `RedirectResponse` 会验证 URL 的安全性，防止开放重定向漏洞。URL 必须包含完整的 scheme 和 netloc。

### StreamingResponse - 流式响应

用于流式传输数据，适合大文件传输或实时数据流。

```python
import typing as t
import asyncio
from unfazed.http import StreamingResponse

# 异步生成器
async def async_data_stream() -> t.AsyncGenerator[bytes, None]:
    """异步数据流"""
    for i in range(10):
        data = f"数据块 {i}\n"
        yield data.encode()
        await asyncio.sleep(0.1)  # 模拟处理延迟

async def stream_async(request: HttpRequest) -> StreamingResponse:
    """异步流式响应"""
    return StreamingResponse(
        content=async_data_stream(),
        media_type="text/plain"
    )

# 同步生成器
def sync_data_stream() -> t.Generator[bytes, None, None]:
    """同步数据流"""
    for i in range(5):
        yield f"同步数据 {i}\n".encode()

async def stream_sync(request: HttpRequest) -> StreamingResponse:
    """同步流式响应"""
    return StreamingResponse(
        content=sync_data_stream(),
        media_type="text/plain"
    )

# 大文件流式传输
async def large_file_stream(file_path: str) -> t.AsyncGenerator[bytes, None]:
    """大文件流式读取"""
    chunk_size = 8192
    async with aiofiles.open(file_path, 'rb') as f:
        while chunk := await f.read(chunk_size):
            yield chunk

async def stream_large_file(request: HttpRequest) -> StreamingResponse:
    """流式传输大文件"""
    file_path = "/path/to/large/file.txt"
    return StreamingResponse(
        content=large_file_stream(file_path),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": "attachment; filename=large_file.txt"
        }
    )

# 实时数据流
async def realtime_data() -> t.AsyncGenerator[str, None]:
    """实时数据生成器"""
    import time
    while True:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        data = f"data: {{\"timestamp\": \"{timestamp}\", \"value\": {time.time()}}}\n\n"
        yield data
        await asyncio.sleep(1)

async def server_sent_events(request: HttpRequest) -> StreamingResponse:
    """Server-Sent Events (SSE) 流"""
    return StreamingResponse(
        content=realtime_data(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )
```

### FileResponse - 文件响应

用于文件下载，内置断点续传支持和 HTTP Range 请求处理。

```python
from unfazed.http import FileResponse
import os
from pathlib import Path

async def download_file(request: HttpRequest) -> FileResponse:
    """基本文件下载"""
    file_path = "/path/to/document.pdf"
    return FileResponse(file_path)

async def download_with_custom_filename(request: HttpRequest) -> FileResponse:
    """自定义下载文件名"""
    file_path = "/data/reports/2024_annual_report.pdf"
    return FileResponse(
        path=file_path,
        filename="年度报告2024.pdf"
    )

async def download_with_custom_chunk_size(request: HttpRequest) -> FileResponse:
    """自定义块大小"""
    file_path = "/large_files/video.mp4"
    return FileResponse(
        path=file_path,
        filename="movie.mp4",
        chunk_size=1024 * 1024,  # 1MB 块
        headers={"X-Custom-Header": "file-download"}
    )

async def conditional_file_download(request: HttpRequest) -> FileResponse:
    """条件文件下载"""
    file_id = request.path_params.get("file_id")
    
    # 根据文件ID确定文件路径
    file_mapping = {
        "report1": "/files/reports/report1.xlsx",
        "image1": "/files/images/photo1.jpg",
        "doc1": "/files/documents/manual.pdf"
    }
    
    file_path = file_mapping.get(file_id)
    if not file_path or not os.path.exists(file_path):
        # 如果文件不存在，可以返回404错误
        # 这里简化处理，实际应该返回适当的错误响应
        raise FileNotFoundError(f"File {file_id} not found")
    
    # 根据文件类型设置不同的文件名
    filename_mapping = {
        "report1": "月度报告.xlsx",
        "image1": "产品图片.jpg", 
        "doc1": "用户手册.pdf"
    }
    
    return FileResponse(
        path=file_path,
        filename=filename_mapping.get(file_id, "download")
    )

# 处理大文件下载的高级示例
async def secure_file_download(request: HttpRequest) -> FileResponse:
    """安全文件下载（带权限检查）"""
    file_id = request.path_params.get("file_id")
    
    # 权限检查（示例）
    try:
        user = request.user
        if not user or not user.has_permission(f"download_file_{file_id}"):
            return JsonResponse({"error": "无权限下载此文件"}, status_code=403)
    except ValueError:
        return JsonResponse({"error": "需要登录"}, status_code=401)
    
    # 文件路径解析
    secure_base_path = Path("/secure/files")
    file_path = secure_base_path / f"{file_id}.pdf"
    
    # 防止路径遍历攻击
    if not str(file_path.resolve()).startswith(str(secure_base_path.resolve())):
        return JsonResponse({"error": "非法文件路径"}, status_code=400)
    
    if not file_path.exists():
        return JsonResponse({"error": "文件未找到"}, status_code=404)
    
    return FileResponse(
        path=file_path,
        filename=f"document_{file_id}.pdf",
        headers={
            "X-Download-Source": "secure-storage",
            "X-File-ID": file_id
        }
    )
```

**FileResponse 特性**:
- **自动断点续传**: 支持 HTTP Range 请求，允许客户端断点下载
- **文件元数据**: 自动设置 ETag、Last-Modified、Content-Length 等头部
- **安全性**: 基于文件路径的访问控制和验证
- **性能优化**: 流式传输，不会将整个文件加载到内存

## 高级用法

### 背景任务

在响应发送后执行清理或异步任务：

```python
from starlette.background import BackgroundTask
import logging

async def log_access(user_id: int, resource: str):
    """记录访问日志的背景任务"""
    logging.info(f"User {user_id} accessed {resource}")
    # 这里可以写入数据库或发送到消息队列

async def send_notification(email: str, message: str):
    """发送通知的背景任务"""
    # 模拟发送邮件
    print(f"Sending email to {email}: {message}")

async def api_with_background_tasks(request: HttpRequest) -> JsonResponse:
    """带多个背景任务的API"""
    # 创建多个背景任务
    tasks = BackgroundTask(log_access, user_id=123, resource="/api/data")
    tasks.add_task(send_notification, "user@example.com", "数据已更新")
    
    return JsonResponse(
        {"message": "操作完成", "status": "success"},
        background=tasks
    )
```

### 条件响应

根据请求条件返回不同类型的响应：

```python
async def conditional_response(request: HttpRequest) -> HttpResponse:
    """根据Accept头返回不同格式"""
    accept_header = request.headers.get("accept", "")
    
    data = {"message": "Hello, World!", "timestamp": "2024-01-01T00:00:00Z"}
    
    if "application/json" in accept_header:
        return JsonResponse(data)
    elif "text/html" in accept_header:
        html_content = f"""
        <html>
        <body>
            <h1>{data['message']}</h1>
            <p>时间: {data['timestamp']}</p>
        </body>
        </html>
        """
        return HtmlResponse(html_content)
    elif "text/plain" in accept_header:
        text_content = f"{data['message']}\n时间: {data['timestamp']}"
        return PlainTextResponse(text_content)
    else:
        # 默认返回JSON
        return JsonResponse(data)
```

### 自定义响应类

创建自定义响应类以满足特殊需求：

```python
import xml.etree.ElementTree as ET
from unfazed.http import HttpResponse

class XmlResponse(HttpResponse):
    """XML响应类"""
    media_type = "application/xml"
    
    def __init__(self, data: dict, **kwargs):
        # 将字典转换为XML
        root = ET.Element("response")
        self._dict_to_xml(data, root)
        xml_content = ET.tostring(root, encoding='unicode')
        super().__init__(content=xml_content, **kwargs)
    
    def _dict_to_xml(self, data: dict, parent: ET.Element):
        """递归将字典转换为XML元素"""
        for key, value in data.items():
            child = ET.SubElement(parent, key)
            if isinstance(value, dict):
                self._dict_to_xml(value, child)
            elif isinstance(value, list):
                for item in value:
                    item_elem = ET.SubElement(child, "item")
                    if isinstance(item, dict):
                        self._dict_to_xml(item, item_elem)
                    else:
                        item_elem.text = str(item)
            else:
                child.text = str(value)

async def xml_response(request: HttpRequest) -> XmlResponse:
    """返回XML响应"""
    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ],
        "total": 2
    }
    return XmlResponse(data)

class CsvResponse(HttpResponse):
    """CSV响应类"""
    media_type = "text/csv"
    
    def __init__(self, data: list, filename: str = "data.csv", **kwargs):
        import io
        import csv
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys() if data else [])
        writer.writeheader()
        writer.writerows(data)
        
        csv_content = output.getvalue()
        headers = kwargs.pop("headers", {})
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'
        
        super().__init__(content=csv_content, headers=headers, **kwargs)

async def csv_export(request: HttpRequest) -> CsvResponse:
    """导出CSV文件"""
    data = [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 35}
    ]
    return CsvResponse(data, filename="users.csv")
```

通过 Unfazed 的响应系统，您可以构建出功能丰富、性能优异的 HTTP API。系统提供了从简单文本响应到复杂文件流传输的完整解决方案，同时保持了良好的扩展性和可定制性。

