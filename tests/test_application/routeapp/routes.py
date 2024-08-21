from unfazed.route import include, path


async def foo(request):
    return {"message": "Hello World!"}


patterns = [
    path(
        "/api/success",
        routes=include("tests.test_application.success.routes"),
    ),
    path("/api/mainapp/foo", endpoint=foo),
]
