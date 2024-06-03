from test_app.urls import urlpatterns as test_app_urlpatterns

from unfazed.route import path

urlpatterns = [
    path("/test_app", test_app_urlpatterns),
]
