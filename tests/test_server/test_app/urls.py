from unfazed.route import path

from .views import hello

urlpatterns = [path("/hello", hello)]
