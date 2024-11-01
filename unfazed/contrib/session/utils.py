import http.cookies
import typing as t


def build_cookie(
    key: str,
    value: str,
    *,
    max_age: int | None = None,
    expires: str | None = None,
    path: str | None = "/",
    domain: str | None = None,
    secure: bool = False,
    httponly: bool = True,
    samesite: t.Literal["lax", "strict", "none"] | None = "lax",
) -> str:
    cookie: http.cookies.BaseCookie[str] = http.cookies.SimpleCookie()
    cookie[key] = value
    if max_age is not None:
        cookie[key]["max-age"] = max_age
    if expires is not None:
        cookie[key]["expires"] = expires
    if path is not None:
        cookie[key]["path"] = path
    if domain is not None:
        cookie[key]["domain"] = domain
    if secure:
        cookie[key]["secure"] = True
    if httponly:
        cookie[key]["httponly"] = True
    if samesite is not None:
        cookie[key]["samesite"] = samesite
    cookie_val = cookie.output(header="").strip()
    return cookie_val
