import sys
import time
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Remove default loguru handler
logger.remove()

# Stderr sink with colors
logger.add(
    sys.stderr,
    colorize=True,
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    level="DEBUG",
)

# File sink without colors
logger.add(
    "logs/app.log",
    rotation="10 MB",
    retention="7 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    enqueue=True,
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        t0 = time.time()
        response = await call_next(request)
        elapsed_ms = (time.time() - t0) * 1000
        logger.info(
            f"{request.method} {request.url.path} ΓåÆ {response.status_code} "
            f"({elapsed_ms:.1f}ms)"
        )
        return response
