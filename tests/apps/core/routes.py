from unfazed.route import path


async def foo(request):
    return {"message": "Hello World!"}


patterns = [path("/foo", endpoint=foo)]
