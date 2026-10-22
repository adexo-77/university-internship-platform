"""Cross-Site Request Forgery (CSRF) defence middleware."""

from urllib.parse import urlparse

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


class CSRFMiddleware(BaseHTTPMiddleware):
    """Origin and Referer checking middleware for state-changing HTTP methods."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method not in SAFE_METHODS:
            allowed = {o.rstrip("/") for o in settings.CORS_ORIGINS}
            origin = request.headers.get("origin")
            if origin:
                if origin.rstrip("/") not in allowed:
                    return JSONResponse(
                        status_code=403,
                        content={
                            "detail": "Cross-origin request forbidden",
                            "code": "CSRF_FORBIDDEN",
                        },
                    )
            else:
                referer = request.headers.get("referer")
                if referer:
                    try:
                        parsed = urlparse(referer)
                        referer_origin = f"{parsed.scheme}://{parsed.netloc}".rstrip("/")
                    except Exception:
                        referer_origin = ""
                    if referer_origin not in allowed:
                        return JSONResponse(
                            status_code=403,
                            content={
                                "detail": "Cross-origin request forbidden",
                                "code": "CSRF_FORBIDDEN",
                            },
                        )

        return await call_next(request)
