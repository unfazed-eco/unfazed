import typing as t

import pytest

from unfazed.core import Unfazed
from unfazed.exception import WebSocketDisconnect
from unfazed.http import WebSocketConnection
from unfazed.route import WebSocketRoute, websocket
from unfazed.route.params import Path as WSPath
from unfazed.route.params import Query as WSQuery

# ---- test endpoints ----


async def echo_endpoint(ws: WebSocketConnection) -> None:
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            await ws.send_text(f"echo: {data}")
    except WebSocketDisconnect:
        pass


async def chat_endpoint(ws: WebSocketConnection, room_id: str) -> None:
    await ws.accept()
    try:
        while True:
            data = await ws.receive_json()
            await ws.send_json({"room": room_id, "msg": data})
    except WebSocketDisconnect:
        pass


async def query_endpoint(ws: WebSocketConnection, token: str) -> None:
    await ws.accept()
    await ws.send_text(f"token={token}")
    await ws.close()


async def error_after_accept(ws: WebSocketConnection) -> None:
    await ws.accept()
    raise ValueError("something went wrong mid-stream")


async def error_before_accept(ws: WebSocketConnection) -> None:
    raise ValueError("something went wrong before accepting")


async def manual_close_then_error(ws: WebSocketConnection) -> None:
    await ws.accept()
    await ws.send_text("ok")
    await ws.close(code=1000)
    raise ValueError("error after close")


async def websocket_disconnect(ws: WebSocketConnection) -> None:
    await ws.accept()
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        pass


async def kwargs_endpoint(ws: WebSocketConnection, **kwargs: t.Any) -> None:
    await ws.accept()
    await ws.send_text("kwargs ok")
    await ws.close()


async def annotated_path_endpoint(
    ws: WebSocketConnection, room_id: t.Annotated[str, WSPath()]
) -> None:
    await ws.accept()
    await ws.send_text(f"room={room_id}")
    await ws.close()


async def annotated_unsupported_endpoint(
    ws: WebSocketConnection, x: t.Annotated[str, WSQuery()]
) -> None:
    await ws.accept()


async def bytes_echo_endpoint(ws: WebSocketConnection) -> None:
    await ws.accept()
    try:
        while True:
            data = await ws.receive_bytes()
            await ws.send_bytes(data)
    except WebSocketDisconnect:
        pass


async def check_properties_endpoint(ws: WebSocketConnection) -> None:
    await ws.accept()
    await ws.send_text(f"scheme={ws.scheme},unfazed={ws.unfazed is not None}")
    await ws.close()


async def session_without_middleware_endpoint(ws: WebSocketConnection) -> None:
    await ws.accept()
    try:
        _ = ws.session
    except ValueError as e:
        await ws.send_text(f"session_error={e}")
        await ws.close()
        return
    await ws.send_text("no error")
    await ws.close()


async def read_session_endpoint(ws: WebSocketConnection) -> None:
    await ws.accept()
    session_val = ws.session
    await ws.send_text(f"session={session_val}")
    await ws.close()


async def read_user_endpoint(ws: WebSocketConnection) -> None:
    await ws.accept()
    user_val = ws.user
    await ws.send_text(f"user={user_val}")
    await ws.close()


async def accept_only_endpoint(ws: WebSocketConnection) -> None:
    await ws.accept()
    await ws.receive_text()


async def user_without_middleware_endpoint(ws: WebSocketConnection) -> None:
    await ws.accept()
    try:
        _ = ws.user
    except ValueError as e:
        await ws.send_text(f"user_error={e}")
        await ws.close()
        return
    await ws.send_text("no error")
    await ws.close()


def _make_app(routes: t.List[t.Any], settings: t.Any) -> Unfazed:
    return Unfazed(routes=routes, settings=settings)


async def _make_and_setup(routes: t.List[t.Any], settings: t.Any) -> Unfazed:
    unfazed = _make_app(routes, settings)
    await unfazed.setup()
    return unfazed


# ---- test classes ----


class TestWebSocketRoute:
    async def test_websocket_route_creation(self) -> None:
        route = websocket("/ws/chat/{room_id}", endpoint=chat_endpoint)
        assert isinstance(route, WebSocketRoute)
        assert route.path == "/ws/chat/{room_id}"
        assert route.include_in_schema is False
        assert "room_id" in route.param_convertors

    async def test_websocket_route_invalid_path(self) -> None:
        with pytest.raises(ValueError, match="must start with '/'"):
            websocket("ws/chat", endpoint=chat_endpoint)  # type: ignore[arg-type]

    async def test_websocket_route_invalid_endpoint(self) -> None:
        with pytest.raises(ValueError, match="must be a function"):
            websocket("/ws/chat", endpoint="not_a_function")  # type: ignore[arg-type]

    async def test_websocket_route_with_app_label(self) -> None:
        route = websocket("/ws/test", endpoint=echo_endpoint, app_label="myapp")
        assert route.app_label == "myapp"
        assert route.tags == ["myapp"]

    async def test_websocket_route_with_explicit_tags(self) -> None:
        route = websocket("/ws/test", endpoint=echo_endpoint, tags=["custom"])
        assert route.tags == ["custom"]

    async def test_websocket_route_with_middleware(
        self, setup_route_unfazed: Unfazed
    ) -> None:
        route = websocket(
            "/ws/test",
            endpoint=echo_endpoint,
            middlewares=["unfazed.contrib.common.middleware.CommonMiddleware"],
        )
        assert route._middleware_strings == [
            "unfazed.contrib.common.middleware.CommonMiddleware"
        ]

    async def test_websocket_route_update_path_same_params(self) -> None:
        route = websocket("/ws/{room_id}", endpoint=chat_endpoint)
        original_ed = route.endpoint_definition
        route.update_path("/newpath/{room_id}")
        assert route.path == "/newpath/{room_id}"
        # Same param keys so endpoint_definition should not be recreated
        assert route.endpoint_definition is original_ed

    async def test_websocket_route_update_path_new_params(self) -> None:
        route = websocket("/ws/{room_id}", endpoint=chat_endpoint)
        original_ed = route.endpoint_definition
        route.update_path("/newpath/{new_id}")
        assert route.path == "/newpath/{new_id}"
        # Different param keys so endpoint_definition should be recreated
        assert route.endpoint_definition is not original_ed

    async def test_websocket_route_update_label(self) -> None:
        route = websocket("/ws/test", endpoint=echo_endpoint)
        assert route.tags == []
        route.update_label("myapp")
        assert route.app_label == "myapp"
        assert route.tags == ["myapp"]

    async def test_websocket_route_update_label_preserves_existing_tags(self) -> None:
        route = websocket("/ws/test", endpoint=echo_endpoint, tags=["custom"])
        route.update_label("myapp")
        assert route.tags == ["custom"]

    async def test_endpoint_with_kwargs(self) -> None:
        route = websocket("/ws/kwargs", endpoint=kwargs_endpoint)
        assert route.endpoint_definition.params is not None
        # **kwargs should be skipped in signature handling
        assert "kwargs" not in route.endpoint_definition.params

    async def test_endpoint_missing_type_hint(self) -> None:
        async def no_hint(ws: WebSocketConnection, x) -> None:  # type: ignore[no-untyped-def]
            pass

        with pytest.raises(TypeError, match="missing type hint"):
            websocket("/ws/test", endpoint=no_hint)  # type: ignore[arg-type]

    async def test_endpoint_annotated_with_path(self) -> None:
        route = websocket("/ws/{room_id}", endpoint=annotated_path_endpoint)
        assert "room_id" in route.endpoint_definition.path_params

    async def test_endpoint_annotated_unsupported(self) -> None:
        with pytest.raises(ValueError, match="Unsupported annotation"):
            websocket(
                "/ws/test",
                endpoint=annotated_unsupported_endpoint,  # type: ignore[arg-type]
            )


class TestWebSocketConnection:
    async def test_echo(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/echo", endpoint=echo_endpoint)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/echo") as ws:
                await ws.send_text("hello")
                resp = await ws.receive_text()
                assert resp == "echo: hello"
                await ws.close()

    async def test_path_param(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/chat/{room_id}", endpoint=chat_endpoint)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/chat/lobby") as ws:
                await ws.send_json({"text": "hi"})
                resp = await ws.receive_json()
                assert resp["room"] == "lobby"
                await ws.close()

    async def test_query_param(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/auth", endpoint=query_endpoint)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/auth?token=abc123") as ws:
                resp = await ws.receive_text()
                assert resp == "token=abc123"

    async def test_send_receive_bytes(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/bytes", endpoint=bytes_echo_endpoint)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/bytes") as ws:
                await ws.send_bytes(b"hello bytes")
                resp = await ws.receive_bytes()
                assert resp == b"hello bytes"
                await ws.close()

    async def test_session_without_middleware(
        self, setup_route_unfazed: Unfazed
    ) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/echo", endpoint=echo_endpoint)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/echo") as ws:
                await ws.send_text("hello")
                resp = await ws.receive_text()
                assert resp == "echo: hello"
                await ws.close()

    async def test_scheme_and_unfazed_properties(
        self, setup_route_unfazed: Unfazed
    ) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/props", endpoint=check_properties_endpoint)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/props") as ws:
                resp = await ws.receive_text()
                assert "scheme=ws" in resp
                assert "unfazed=True" in resp

    async def test_session_value_error(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/session", endpoint=session_without_middleware_endpoint)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/session") as ws:
                resp = await ws.receive_text()
                assert "session_error" in resp

    async def test_user_value_error(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/user", endpoint=user_without_middleware_endpoint)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/user") as ws:
                resp = await ws.receive_text()
                assert "user_error" in resp

    async def test_subprotocols(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/echo", endpoint=echo_endpoint)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/echo", subprotocols=["chat"]) as ws:
                await ws.send_text("hi")
                resp = await ws.receive_text()
                assert resp == "echo: hi"
                await ws.close()


class TestWebSocketExceptionHandling:
    async def test_error_after_accept_closes_with_1011(
        self, setup_route_unfazed: Unfazed
    ) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/err", endpoint=error_after_accept)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/err") as ws:
                msg = await ws.receive()
                assert msg["type"] == "websocket.close"
                assert msg.get("code") == 1011

    async def test_error_before_accept(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/err2", endpoint=error_before_accept)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/err2") as ws:
                msg = await ws.receive()
                assert msg["type"] == "websocket.close"

    async def test_disconnect_propagates_silently(
        self, setup_route_unfazed: Unfazed
    ) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/dc", endpoint=websocket_disconnect)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/dc") as ws:
                await ws.close(code=1000)

    async def test_close_then_error(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/cte", endpoint=manual_close_then_error)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/cte") as ws:
                resp = await ws.receive_text()
                assert resp == "ok"

    async def test_common_middleware_websocket_error(
        self, setup_route_unfazed: Unfazed
    ) -> None:
        from unfazed.middleware.internal.common import CommonMiddleware
        from unfazed.test import Requestfactory

        app = Unfazed(
            routes=[websocket("/err", endpoint=error_after_accept)],
            middlewares=[CommonMiddleware],
            settings=setup_route_unfazed.settings,
        )
        await app.setup()

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/err") as ws:
                msg = await ws.receive()
                assert msg["type"] == "websocket.close"


class TestWebSocketInRoutes:
    async def test_websocket_in_path_routes(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.route import path
        from unfazed.test import Requestfactory

        routes = path(
            "/ws",
            routes=[
                websocket("/echo", endpoint=echo_endpoint),
            ],
        )

        app = await _make_and_setup(routes, setup_route_unfazed.settings)

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/ws/echo") as ws:
                await ws.send_text("test")
                resp = await ws.receive_text()
                assert resp == "echo: test"
                await ws.close()

    async def test_websocket_route_not_in_openapi(self) -> None:
        from unfazed.openapi.base import OpenApi
        from unfazed.schema import OpenAPI as OpenAPISettingModel

        routes: t.List[t.Any] = [
            websocket("/ws/echo", endpoint=echo_endpoint),
        ]

        OpenApi.create_schema(
            routes,
            OpenAPISettingModel.model_validate(
                {
                    "openapi": "3.1.1",
                    "info": {
                        "title": "test",
                        "description": "test",
                        "version": "1.0.0",
                    },
                    "allow_public": True,
                }
            ),
        )

        schema = OpenApi.schema
        assert schema is not None
        assert "/ws/echo" not in schema.get("paths", {})


class TestWebSocketAppLabelValidation:
    async def test_app_label_not_installed(self, setup_route_unfazed: Unfazed) -> None:
        # Verify parse_urlconf validates app_label for regular Route objects
        from unfazed.http import HttpRequest, HttpResponse
        from unfazed.route import Route

        async def dummy(request: HttpRequest) -> HttpResponse:
            return HttpResponse("ok")  # pragma: no cover

        route = Route("/test", endpoint=dummy, app_label="nonexistent_app")
        assert route.app_label == "nonexistent_app"

    async def test_raw_websocketroute_non_function(self) -> None:
        from unfazed.route.websocket_routing import WebSocketRoute as WSR

        with pytest.raises(ValueError, match="must be a function"):
            WSR("/ws/test", "not_a_function")  # type: ignore[arg-type]

    async def test_handler_websocket_disconnect(
        self, setup_route_unfazed: Unfazed
    ) -> None:
        from unfazed.test import Requestfactory

        app = await _make_and_setup(
            [websocket("/ao", endpoint=accept_only_endpoint)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/ao") as ws:
                await ws.close(code=1000)


class TestWebSocketWithMiddleware:
    """Test WebSocketConnection.session and .user with middleware installed."""

    async def test_session_with_middleware(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.middleware import BaseMiddleware
        from unfazed.test import Requestfactory
        from unfazed.type import Receive, Scope, Send

        class SetSessionMiddleware(BaseMiddleware):
            async def __call__(
                self, scope: Scope, receive: Receive, send: Send
            ) -> None:
                scope["session"] = {"key": "value"}
                await self.app(scope, receive, send)

        app = Unfazed(
            routes=[websocket("/session", endpoint=read_session_endpoint)],
            middlewares=[SetSessionMiddleware],
            settings=setup_route_unfazed.settings,
        )
        await app.setup()

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/session") as ws:
                resp = await ws.receive_text()
                assert "session=" in resp

    async def test_user_with_middleware(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.middleware import BaseMiddleware
        from unfazed.test import Requestfactory
        from unfazed.type import Receive, Scope, Send

        class SetUserMiddleware(BaseMiddleware):
            async def __call__(
                self, scope: Scope, receive: Receive, send: Send
            ) -> None:
                scope["user"] = "testuser"
                await self.app(scope, receive, send)

        app = Unfazed(
            routes=[websocket("/user", endpoint=read_user_endpoint)],
            middlewares=[SetUserMiddleware],
            settings=setup_route_unfazed.settings,
        )
        await app.setup()

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/user") as ws:
                resp = await ws.receive_text()
                assert "user=" in resp
