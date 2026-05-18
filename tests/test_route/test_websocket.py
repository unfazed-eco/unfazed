import typing as t

import pytest
from starlette.websockets import WebSocketDisconnect

from unfazed.core import Unfazed
from unfazed.http import WebSocketConnection
from unfazed.route import WebSocketRoute, websocket


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


async def _make_app(routes: t.List[t.Any], settings: t.Any) -> Unfazed:
    """Helper to create and set up an Unfazed app with custom routes."""
    unfazed = Unfazed(routes=routes, settings=settings)
    await unfazed.setup()
    return unfazed


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


class TestWebSocketConnection:
    async def test_echo(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.test import Requestfactory

        app = await _make_app(
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

        app = await _make_app(
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

        app = await _make_app(
            [websocket("/auth", endpoint=query_endpoint)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/auth?token=abc123") as ws:
                resp = await ws.receive_text()
                assert resp == "token=abc123"


class TestWebSocketExceptionHandling:
    async def test_error_after_accept_closes_with_1011(
        self, setup_route_unfazed: Unfazed
    ) -> None:
        from unfazed.test import Requestfactory

        app = await _make_app(
            [websocket("/err", endpoint=error_after_accept)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/err") as ws:
                msg = await ws.receive()
                # Layer 1 should send close(1011) on unexpected error
                assert msg["type"] == "websocket.close"
                assert msg.get("code") == 1011

    async def test_error_before_accept(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.test import Requestfactory

        app = await _make_app(
            [websocket("/err2", endpoint=error_before_accept)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/err2") as ws:
                msg = await ws.receive()
                # Layer 1 should send close on error before accept
                assert msg["type"] == "websocket.close"

    async def test_disconnect_propagates_silently(
        self, setup_route_unfazed: Unfazed
    ) -> None:
        from unfazed.test import Requestfactory

        app = await _make_app(
            [websocket("/dc", endpoint=websocket_disconnect)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/dc") as ws:
                await ws.close(code=1000)

    async def test_close_then_error(self, setup_route_unfazed: Unfazed) -> None:
        from unfazed.test import Requestfactory

        app = await _make_app(
            [websocket("/cte", endpoint=manual_close_then_error)],
            setup_route_unfazed.settings,
        )

        async with Requestfactory(app, lifespan_on=False) as client:
            async with client.websocket_connect("/cte") as ws:
                resp = await ws.receive_text()
                assert resp == "ok"
                # After user closes, error should not cause double close
                # The session should end cleanly


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

        app = await _make_app(routes, setup_route_unfazed.settings)

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
