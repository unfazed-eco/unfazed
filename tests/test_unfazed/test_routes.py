from unfazed.core import Unfazed


def test_route_collect():
    unfazed = Unfazed()
    unfazed.setup_routes()

    routes = unfazed.router.routes

    assert len(routes) == 2
