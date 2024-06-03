from unfazed.route import path


async def home(request):
    return "Home"


async def subpage1(request):
    return "Subpage 1"


async def subpage2(request):
    return "Subpage 2"


subpaths = [
    path("/subpage1", subpage1),
    path("/subpage2", subpage2),
]

urlpatterns = [
    path("/", home),
    path("/about", subpaths),
]
