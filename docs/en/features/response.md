Unfazed HttpResponse
====

Unfazed provides a complete HTTP response class system, based on Starlette's response classes with enhanced functionality. All view functions must return objects of type `HttpResponse`.

## Response System Overview

### Core Features

- **Multiple Response Types**: Supports text, HTML, JSON, file, streaming responses and more
- **High-Performance JSON**: Uses orjson to provide high-performance JSON serialization
- **File Resume Support**: Built-in HTTP Range request support for resumable downloads
- **Streaming Response**: Supports asynchronous streaming data transmission, suitable for large files and real-time data
- **Automatic Header Handling**: Automatically sets correct Content-Type and other necessary headers
- **Background Tasks**: Supports background tasks executed after response is sent

### Response Type Hierarchy

```python
HttpResponse (Base response class)
├── PlainTextResponse (Plain text response)
├── HtmlResponse (HTML response)
├── JsonResponse (JSON response)
├── RedirectResponse (Redirect response)
├── StreamingResponse (Streaming response)
└── FileResponse (File response, inherits from StreamingResponse)
```

### Basic Signature

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

## Basic Usage

### Simple Example

```python
from unfazed.http import HttpRequest, HttpResponse, JsonResponse
from starlette.background import BackgroundTask

async def simple_response(request: HttpRequest) -> HttpResponse:
    """Simplest response"""
    return HttpResponse("Hello, World!")

async def with_status_and_headers(request: HttpRequest) -> HttpResponse:
    """Response with status code and headers"""
    return HttpResponse(
        content="Custom response",
        status_code=201,
        headers={"X-Custom-Header": "MyValue"},
        media_type="text/plain; charset=utf-8"
    )

def cleanup_task():
    """Background task example"""
    print("Cleanup task executed after response is sent")

async def with_background_task(request: HttpRequest) -> HttpResponse:
    """Response with background task"""
    task = BackgroundTask(cleanup_task)
    return HttpResponse(
        content="Task submitted",
        background=task
    )
```

## Response Types Details

### PlainTextResponse - Plain Text Response

Used to return plain text content, Content-Type is `text/plain`.

```python
from unfazed.http import PlainTextResponse

async def text_response(request: HttpRequest) -> PlainTextResponse:
    """Return plain text"""
    return PlainTextResponse("This is a plain text response")

async def text_with_encoding(request: HttpRequest) -> PlainTextResponse:
    """Text response with specified encoding"""
    return PlainTextResponse(
        content="Text response with encoding",
        headers={"Content-Type": "text/plain; charset=utf-8"}
    )

async def multiline_text(request: HttpRequest) -> PlainTextResponse:
    """Multiline text response"""
    text_content = """
    This is a multiline text response
    Second line content
    Third line content
    """
    return PlainTextResponse(text_content.strip())
```

### HtmlResponse - HTML Response

Used to return HTML content, Content-Type is `text/html`.

```python
from unfazed.http import HtmlResponse

async def html_page(request: HttpRequest) -> HtmlResponse:
    """Return HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Unfazed HTML Response</title>
        <meta charset="utf-8">
    </head>
    <body>
        <h1>Welcome to Unfazed</h1>
        <p>This is an HTML response example</p>
    </body>
    </html>
    """
    return HtmlResponse(html_content)

async def dynamic_html(request: HttpRequest) -> HtmlResponse:
    """Dynamic HTML content"""
    user_name = request.query_params.get("name", "Guest")
    html_content = f"""
    <html>
    <body>
        <h1>Hello, {user_name}!</h1>
        <p>Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </body>
    </html>
    """
    return HtmlResponse(html_content)

async def error_page(request: HttpRequest) -> HtmlResponse:
    """Error page"""
    error_html = """
    <html>
    <body style="font-family: Arial;">
        <h1 style="color: red;">404 - Page Not Found</h1>
        <p>Sorry, the page you are looking for does not exist.</p>
        <a href="/">Return to Home</a>
    </body>
    </html>
    """
    return HtmlResponse(error_html, status_code=404)
```

### JsonResponse - JSON Response

Used to return JSON data, supports automatic serialization of dictionaries, lists, and Pydantic models.

```python
from unfazed.http import JsonResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Basic usage
async def json_dict(request: HttpRequest) -> JsonResponse:
    """Return dictionary"""
    return JsonResponse({"message": "Hello, World!", "status": "success"})

async def json_list(request: HttpRequest) -> JsonResponse:
    """Return list"""
    return JsonResponse([1, 2, 3, {"name": "item"}])

# Pydantic models
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
    """Return Pydantic model"""
    user = User(
        id=1,
        username="john_doe",
        email="john@example.com"
    )
    return JsonResponse(user)

async def json_complex_model(request: HttpRequest) -> JsonResponse:
    """Return complex model"""
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

# Custom status code and headers
async def json_with_custom_headers(request: HttpRequest) -> JsonResponse:
    """JSON response with custom headers"""
    data = {"message": "Resource created", "id": 123}
    return JsonResponse(
        content=data,
        status_code=201,
        headers={
            "Location": "/api/resources/123",
            "X-Resource-ID": "123"
        }
    )

# Error response
async def json_error(request: HttpRequest) -> JsonResponse:
    """JSON error response"""
    error_data = {
        "error": "Parameter validation failed",
        "code": "VALIDATION_ERROR",
        "details": {
            "field": "email",
            "message": "Email format is incorrect"
        }
    }
    return JsonResponse(error_data, status_code=400)
```

### RedirectResponse - Redirect Response

Used for HTTP redirects, automatically handles URL encoding and security validation.

```python
from unfazed.http import RedirectResponse

async def temporary_redirect(request: HttpRequest) -> RedirectResponse:
    """Temporary redirect (302)"""
    return RedirectResponse("https://www.example.com")

async def permanent_redirect(request: HttpRequest) -> RedirectResponse:
    """Permanent redirect (301)"""
    return RedirectResponse(
        "https://www.newdomain.com",
        status_code=301
    )

async def login_redirect(request: HttpRequest) -> RedirectResponse:
    """Login redirect"""
    # Check if user is already logged in
    if not hasattr(request, 'user') or not request.user:
        # Redirect to login page and save original URL
        original_url = str(request.url)
        login_url = f"https://auth.example.com/login?next={original_url}"
        return RedirectResponse(login_url)
    
    # User is logged in, redirect to dashboard
    return RedirectResponse("https://app.example.com/dashboard")

async def conditional_redirect(request: HttpRequest) -> RedirectResponse:
    """Conditional redirect"""
    user_agent = request.headers.get("user-agent", "").lower()
    
    if "mobile" in user_agent:
        return RedirectResponse("https://m.example.com")
    else:
        return RedirectResponse("https://www.example.com")
```

**Note**: `RedirectResponse` validates URL security to prevent open redirect vulnerabilities. URL must include complete scheme and netloc.

### StreamingResponse - Streaming Response

Used for streaming data transmission, suitable for large file transfers or real-time data streams.

```python
import typing as t
import asyncio
from unfazed.http import StreamingResponse

# Async generator
async def async_data_stream() -> t.AsyncGenerator[bytes, None]:
    """Async data stream"""
    for i in range(10):
        data = f"Data chunk {i}\n"
        yield data.encode()
        await asyncio.sleep(0.1)  # Simulate processing delay

async def stream_async(request: HttpRequest) -> StreamingResponse:
    """Async streaming response"""
    return StreamingResponse(
        content=async_data_stream(),
        media_type="text/plain"
    )

# Sync generator
def sync_data_stream() -> t.Generator[bytes, None, None]:
    """Sync data stream"""
    for i in range(5):
        yield f"Sync data {i}\n".encode()

async def stream_sync(request: HttpRequest) -> StreamingResponse:
    """Sync streaming response"""
    return StreamingResponse(
        content=sync_data_stream(),
        media_type="text/plain"
    )

# Large file streaming
async def large_file_stream(file_path: str) -> t.AsyncGenerator[bytes, None]:
    """Large file streaming read"""
    chunk_size = 8192
    async with aiofiles.open(file_path, 'rb') as f:
        while chunk := await f.read(chunk_size):
            yield chunk

async def stream_large_file(request: HttpRequest) -> StreamingResponse:
    """Stream large file"""
    file_path = "/path/to/large/file.txt"
    return StreamingResponse(
        content=large_file_stream(file_path),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": "attachment; filename=large_file.txt"
        }
    )

# Real-time data stream
async def realtime_data() -> t.AsyncGenerator[str, None]:
    """Real-time data generator"""
    import time
    while True:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        data = f"data: {{\"timestamp\": \"{timestamp}\", \"value\": {time.time()}}}\n\n"
        yield data
        await asyncio.sleep(1)

async def server_sent_events(request: HttpRequest) -> StreamingResponse:
    """Server-Sent Events (SSE) stream"""
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

### FileResponse - File Response

Used for file downloads, with built-in resume support and HTTP Range request handling.

```python
from unfazed.http import FileResponse
import os
from pathlib import Path

async def download_file(request: HttpRequest) -> FileResponse:
    """Basic file download"""
    file_path = "/path/to/document.pdf"
    return FileResponse(file_path)

async def download_with_custom_filename(request: HttpRequest) -> FileResponse:
    """Custom download filename"""
    file_path = "/data/reports/2024_annual_report.pdf"
    return FileResponse(
        path=file_path,
        filename="Annual Report 2024.pdf"
    )

async def download_with_custom_chunk_size(request: HttpRequest) -> FileResponse:
    """Custom chunk size"""
    file_path = "/large_files/video.mp4"
    return FileResponse(
        path=file_path,
        filename="movie.mp4",
        chunk_size=1024 * 1024,  # 1MB chunk
        headers={"X-Custom-Header": "file-download"}
    )

async def conditional_file_download(request: HttpRequest) -> FileResponse:
    """Conditional file download"""
    file_id = request.path_params.get("file_id")
    
    # Determine file path based on file ID
    file_mapping = {
        "report1": "/files/reports/report1.xlsx",
        "image1": "/files/images/photo1.jpg",
        "doc1": "/files/documents/manual.pdf"
    }
    
    file_path = file_mapping.get(file_id)
    if not file_path or not os.path.exists(file_path):
        # If file doesn't exist, can return 404 error
        # Here simplified handling, should return appropriate error response
        raise FileNotFoundError(f"File {file_id} not found")
    
    # Set different filenames based on file type
    filename_mapping = {
        "report1": "Monthly Report.xlsx",
        "image1": "Product Image.jpg", 
        "doc1": "User Manual.pdf"
    }
    
    return FileResponse(
        path=file_path,
        filename=filename_mapping.get(file_id, "download")
    )

# Advanced example for handling large file downloads
async def secure_file_download(request: HttpRequest) -> FileResponse:
    """Secure file download (with permission check)"""
    file_id = request.path_params.get("file_id")
    
    # Permission check (example)
    try:
        user = request.user
        if not user or not user.has_permission(f"download_file_{file_id}"):
            return JsonResponse({"error": "No permission to download this file"}, status_code=403)
    except ValueError:
        return JsonResponse({"error": "Login required"}, status_code=401)
    
    # File path resolution
    secure_base_path = Path("/secure/files")
    file_path = secure_base_path / f"{file_id}.pdf"
    
    # Prevent path traversal attacks
    if not str(file_path.resolve()).startswith(str(secure_base_path.resolve())):
        return JsonResponse({"error": "Illegal file path"}, status_code=400)
    
    if not file_path.exists():
        return JsonResponse({"error": "File not found"}, status_code=404)
    
    return FileResponse(
        path=file_path,
        filename=f"document_{file_id}.pdf",
        headers={
            "X-Download-Source": "secure-storage",
            "X-File-ID": file_id
        }
    )
```

**FileResponse Features**:
- **Automatic Resume Support**: Supports HTTP Range requests, allows client resume downloads
- **File Metadata**: Automatically sets ETag, Last-Modified, Content-Length headers
- **Security**: File path-based access control and validation
- **Performance Optimization**: Streaming transmission, won't load entire file into memory

## Advanced Usage

### Background Tasks

Execute cleanup or async tasks after response is sent:

```python
from starlette.background import BackgroundTask
import logging

async def log_access(user_id: int, resource: str):
    """Background task to log access"""
    logging.info(f"User {user_id} accessed {resource}")
    # Can write to database or send to message queue here

async def send_notification(email: str, message: str):
    """Background task to send notification"""
    # Simulate sending email
    print(f"Sending email to {email}: {message}")

async def api_with_background_tasks(request: HttpRequest) -> JsonResponse:
    """API with multiple background tasks"""
    # Create multiple background tasks
    tasks = BackgroundTask(log_access, user_id=123, resource="/api/data")
    tasks.add_task(send_notification, "user@example.com", "Data updated")
    
    return JsonResponse(
        {"message": "Operation completed", "status": "success"},
        background=tasks
    )
```

### Conditional Response

Return different types of responses based on request conditions:

```python
async def conditional_response(request: HttpRequest) -> HttpResponse:
    """Return different formats based on Accept header"""
    accept_header = request.headers.get("accept", "")
    
    data = {"message": "Hello, World!", "timestamp": "2024-01-01T00:00:00Z"}
    
    if "application/json" in accept_header:
        return JsonResponse(data)
    elif "text/html" in accept_header:
        html_content = f"""
        <html>
        <body>
            <h1>{data['message']}</h1>
            <p>Time: {data['timestamp']}</p>
        </body>
        </html>
        """
        return HtmlResponse(html_content)
    elif "text/plain" in accept_header:
        text_content = f"{data['message']}\nTime: {data['timestamp']}"
        return PlainTextResponse(text_content)
    else:
        # Default return JSON
        return JsonResponse(data)
```

### Custom Response Classes

Create custom response classes to meet special requirements:

```python
import xml.etree.ElementTree as ET
from unfazed.http import HttpResponse

class XmlResponse(HttpResponse):
    """XML response class"""
    media_type = "application/xml"
    
    def __init__(self, data: dict, **kwargs):
        # Convert dictionary to XML
        root = ET.Element("response")
        self._dict_to_xml(data, root)
        xml_content = ET.tostring(root, encoding='unicode')
        super().__init__(content=xml_content, **kwargs)
    
    def _dict_to_xml(self, data: dict, parent: ET.Element):
        """Recursively convert dictionary to XML elements"""
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
    """Return XML response"""
    data = {
        "users": [
            {"id": 1, "name": "Alice"},
            {"id": 2, "name": "Bob"}
        ],
        "total": 2
    }
    return XmlResponse(data)

class CsvResponse(HttpResponse):
    """CSV response class"""
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
    """Export CSV file"""
    data = [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 35}
    ]
    return CsvResponse(data, filename="users.csv")
```

Through Unfazed's response system, you can build feature-rich, high-performance HTTP APIs. The system provides a complete solution from simple text responses to complex file streaming, while maintaining good extensibility and customizability.
