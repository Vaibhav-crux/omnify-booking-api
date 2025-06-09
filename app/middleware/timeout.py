from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio
import logging

class TimeoutMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, timeout_seconds=10):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds  # Timeout duration in seconds
        self.logger = logging.getLogger("devanchor.middleware.timeout")

    async def dispatch(self, request: Request, call_next):
        try:
            response = await asyncio.wait_for(
                call_next(request),
                timeout=self.timeout_seconds
            )
            return response
        except asyncio.TimeoutError:
            self.logger.error(f"Request timeout after {self.timeout_seconds}s: {request.url}")
            raise HTTPException(
                status_code=504,
                detail="Request Timeout"
            )

def add_timeout_middleware(app):
    app.add_middleware(TimeoutMiddleware)