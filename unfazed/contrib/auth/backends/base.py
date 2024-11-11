from unfazed.http import HttpRequest, HttpResponse


class AuthBaseBackend:
    def pre_login(self, request: HttpRequest) -> None:
        pass

    def post_login(self, request: HttpRequest, response: HttpResponse) -> None:
        pass

    def pre_logout(self, request: HttpRequest) -> None:
        pass

    def post_logout(self, request: HttpRequest, response: HttpResponse) -> None:
        pass
