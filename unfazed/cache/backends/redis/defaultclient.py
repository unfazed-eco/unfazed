import typing as t

from redis.asyncio import Redis
from redis.asyncio.connection import parse_url
from redis.asyncio.retry import Retry
from redis.backoff import ConstantBackoff


class AsyncDefaultBackend(Redis):
    """
    Usage:
        CACHE = {
            "default": {
                "BACKEND": "unfazed.cache.backends.redis.AsyncDefaultBackend",
                "LOCATION": "redis://localhost:6379",
                "OPTIONS": {
                    "retry": True,
                    "max_connections": 10,
                    "health_check_interval": 30
                },
            }
        }

    """

    def __init__(
        self,
        location: str,
        options: t.Optional[t.Dict[str, t.Any]] = None,
    ):
        kw = parse_url(location)
        if options is None:
            options = {}
        retry = options.get("retry", True)
        if retry:
            retry_cls = Retry(ConstantBackoff(0.5), 1)
        else:
            retry_cls = None

        super().__init__(
            host=kw.get("host", "localhost"),
            port=kw.get("port", 6379),
            db=kw.get("db", 0),
            password=kw.get("password", None),
            username=kw.get("username"),
            retry=retry_cls,
            socket_timeout=options.get("socket_timeout"),
            socket_connect_timeout=options.get("socket_connect_timeout"),
            socket_keepalive=options.get("socket_keepalive"),
            socket_keepalive_options=options.get("socket_keepalive_options"),
            decode_responses=options.get("decode_responses", True),
            retry_on_timeout=options.get("retry_on_timeout"),
            retry_on_error=options.get("retry_on_error"),
            max_connections=options.get("max_connections"),
            single_connection_client=options.get("single_connection_client", False),
            health_check_interval=options.get("health_check_interval", 30),
            ssl=options.get("ssl", False),
            ssl_keyfile=options.get("ssl_keyfile"),
            ssl_certfile=options.get("ssl_certfile"),
            ssl_cert_reqs=options.get("ssl_cert_reqs", "required"),
            ssl_ca_certs=options.get("ssl_ca_certs"),
            ssl_ca_data=options.get("ssl_ca_data"),
            ssl_check_hostname=options.get("ssl_check_hostname", False),
            ssl_min_version=options.get("ssl_min_version"),
            ssl_ciphers=options.get("ssl_ciphers"),
        )
