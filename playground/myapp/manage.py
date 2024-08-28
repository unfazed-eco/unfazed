import asyncio
import os
import sys
import warnings

scope = {
    "type": "http",
    "asgi": {"version": "3.0", "spec_version": "2.4"},
    "http_version": "1.1",
    "server": ("172.20.0.4", 9527),
    "client": ("172.20.0.1", 55502),
    "scheme": "http",
    "method": "GET",
    "root_path": "",
    "path": "/api/account/user-list",
    "raw_path": b"/api/account/user-list",
    "query_string": b"",
    "headers": [
        (b"host", b"127.0.0.1:9527"),
        (b"connection", b"keep-alive"),
        (b"cache-control", b"max-age=0"),
        (
            b"sec-ch-ua",
            b'"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        ),
        (b"sec-ch-ua-mobile", b"?0"),
        (b"sec-ch-ua-platform", b'"macOS"'),
        (b"upgrade-insecure-requests", b"1"),
        (
            b"user-agent",
            b"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        ),
        (
            b"accept",
            b"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        ),
        (b"sec-fetch-site", b"none"),
        (b"sec-fetch-mode", b"navigate"),
        (b"sec-fetch-user", b"?1"),
        (b"sec-fetch-dest", b"document"),
        (b"accept-encoding", b"gzip, deflate, br, zstd"),
        (b"accept-language", b"en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7"),
    ],
    "state": {},
}


async def main() -> None:
    root_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(root_path)
    os.environ.setdefault(
        "UNFAZED_SETTINGS_MODULE", "playground.myapp.backend.settings"
    )
    try:
        from unfazed.core import Unfazed

        unfazed = Unfazed()
        await unfazed.setup()
    except ImportError:
        warnings.warn("Could not import unfazed. Did you forget to install it?")
        sys.exit(1)

    except Exception as e:
        warnings.warn(f"An error occurred: {e}")
        sys.exit(1)

    await unfazed.execute_command_from_argv()


if __name__ == "__main__":
    asyncio.run(main())
