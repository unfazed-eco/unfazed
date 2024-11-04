from unfazed.http import HttpRequest, HttpResponse, JsonResponse


async def list_route(request: HttpRequest) -> HttpResponse:
    return JsonResponse(request.app.routes)


async def settings(request: HttpRequest) -> JsonResponse:
    return JsonResponse(request.app.settings)


async def model_desc(request: HttpRequest) -> HttpResponse:
    return JsonResponse(request.app.registry.models)


async def model_detail(request: HttpRequest) -> HttpResponse:
    model_name = request.path_params["model_name"]
    model = request.app.registry.models[model_name]
    return JsonResponse(model.to_route())


async def model_data(request: HttpRequest) -> HttpResponse:
    model_name = request.path_params["model_name"]
    model = request.app.registry.models[model_name]
    data = model.to_serialize()
    return JsonResponse(data)


async def model_action(request: HttpRequest) -> HttpResponse:
    model_name = request.path_params["model_name"]
    model = request.app.registry.models[model_name]
    return JsonResponse(model.get_actions())


async def model_batch_action(request: HttpRequest) -> HttpResponse:
    model_name = request.path_params["model_name"]
    model = request.app.registry.models[model_name]
    return JsonResponse(model.get_batch_actions())


async def model_save(request: HttpRequest) -> HttpResponse:
    model_name = request.path_params["model_name"]
    model = request.app.registry.models[model_name]
    data = await request.json()
    model.save(data)
    return JsonResponse({})


async def model_delete(request: HttpRequest) -> HttpResponse:
    model_name = request.path_params["model_name"]
    model = request.app.registry.models[model_name]
    data = await request.json()
    model.delete(data)
    return JsonResponse({})
