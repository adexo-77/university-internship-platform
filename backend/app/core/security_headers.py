"""Security headers middleware enforcing browser security policies."""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

NO_STORE_PREFIXES = ("/api/auth", "/api/dashboard")


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach defensive security headers to all HTTP responses."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        path = request.url.path
        if any(path.startswith(prefix) for prefix in NO_STORE_PREFIXES):
            response.headers["Cache-Control"] = "no-store"

        return response
