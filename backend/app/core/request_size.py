"""Middleware enforcing maximum HTTP request body size."""

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

MAX_REQUEST_BODY_BYTES = 256 * 1024  # 256 KB


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Enforce a strict 256 KB limit on all incoming HTTP request bodies."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                if int(content_length) > MAX_REQUEST_BODY_BYTES:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "detail": ("Request body exceeds maximum allowed size of 256 KB"),
                            "code": "PAYLOAD_TOO_LARGE",
                        },
                    )
            except ValueError:
                pass

        body = await request.body()
        if len(body) > MAX_REQUEST_BODY_BYTES:
            return JSONResponse(
                status_code=413,
                content={
                    "detail": ("Request body exceeds maximum allowed size of 256 KB"),
                    "code": "PAYLOAD_TOO_LARGE",
                },
            )

        return await call_next(request)
