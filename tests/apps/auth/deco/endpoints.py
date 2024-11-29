from unfazed.contrib.auth.decorators import login_required, permission_required
from unfazed.http import HttpRequest, HttpResponse


@login_required
async def async_login_succeed(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Login success")


@login_required
def login_succeed(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Login success")


@login_required
async def async_login_fail(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Login fail")


@login_required
def login_fail(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Login fail")


@login_required
@permission_required("auth.async_permission_succeed.can_access")
async def async_permission_succeed(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Permission success")


@login_required
@permission_required("auth.permission_succeed.can_access")
def permission_succeed(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Permission success")


@login_required
@permission_required("auth.permission_fail.can_access")
async def async_permission_fail(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Permission fail")


@login_required
@permission_required("auth.permission_fail.can_access")
def permission_fail(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Permission fail")
