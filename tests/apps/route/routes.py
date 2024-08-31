from unfazed.route import include, path


async def foo(request):
    return {"message": "Hello World!"}


patterns = [
    path(
        "/api/success",
        routes=include("tests.apps.route.common.routes"),
    ),
    path("/api/mainapp/foo", endpoint=foo),
]
