"""Cross-Site Request Forgery (CSRF) defence middleware."""

from urllib.parse import urlparse

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def get_public_host(request: Request) -> str:
    """Extract public host of request, trusting X-Forwarded-Host only if TRUSTED_PROXY is True."""
    if settings.TRUSTED_PROXY:
        fwd_host = request.headers.get("x-forwarded-host")
        if fwd_host:
            return fwd_host.split(",")[-1].strip().lower()
    host = request.headers.get("host")
    if host:
        return host.split(",")[-1].strip().lower()
    return ""


def is_allowed_origin(candidate_url: str, request: Request, allowed_origins: set[str]) -> bool:
    """Validate candidate Origin or Referer against allowed list and same-origin public host."""
    if not candidate_url:
        return False
    try:
        parsed = urlparse(candidate_url)
        if not parsed.netloc:
            return False
        candidate_origin = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
        if candidate_origin in allowed_origins:
            return True
        candidate_netloc = parsed.netloc.lower()
        public_host = get_public_host(request)
        if not public_host:
            return False
        if candidate_netloc == public_host:
            return True
        candidate_hostname = parsed.hostname.lower() if parsed.hostname else ""
        public_hostname = public_host.split(":")[0].lower()
        if candidate_hostname and candidate_hostname == public_hostname:
            cand_port = parsed.port or (443 if parsed.scheme == "https" else 80)
            pub_parts = public_host.split(":")
            pub_port = (
                int(pub_parts[1])
                if len(pub_parts) > 1
                else (443 if request.headers.get("x-forwarded-proto") == "https" else 80)
            )
            return cand_port == pub_port
        return False
    except Exception:
        return False


class CSRFMiddleware(BaseHTTPMiddleware):
    """Origin and Referer checking middleware with static and same-origin validation."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method not in SAFE_METHODS:
            allowed = {o.rstrip("/") for o in settings.CORS_ORIGINS}
            origin = request.headers.get("origin")
            if origin:
                if not is_allowed_origin(origin, request, allowed):
                    return JSONResponse(
                        status_code=403,
                        content={
                            "detail": "Cross-origin request forbidden",
                            "code": "CSRF_FORBIDDEN",
                        },
                    )
            else:
                referer = request.headers.get("referer")
                if referer and not is_allowed_origin(referer, request, allowed):
                    return JSONResponse(
                        status_code=403,
                        content={
                            "detail": "Cross-origin request forbidden",
                            "code": "CSRF_FORBIDDEN",
                        },
                    )

        return await call_next(request)
