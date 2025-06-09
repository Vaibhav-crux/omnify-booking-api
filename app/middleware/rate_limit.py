from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
import time
import logging

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests=100, window=60):
        super().__init__(app)
        self.max_requests = max_requests  # Maximum allowed requests
        self.window = window  # Time window in seconds
        self.request_counts = defaultdict(list)  # Track requests per IP
        self.logger = logging.getLogger("devanchor.middleware.rate_limit")

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Remove requests outside the time window
        self.request_counts[client_ip] = [
            t for t in self.request_counts[client_ip]
            if current_time - t < self.window
        ]
        
        # Enforce rate limit
        if len(self.request_counts[client_ip]) >= self.max_requests:
            self.logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Too Many Requests"
            )
        
        # Record current request timestamp
        self.request_counts[client_ip].append(current_time)
        self.logger.debug(f"Request count for {client_ip}: {len(self.request_counts[client_ip])}")
        
        # Process request
        response = await call_next(request)
        return response

def add_rate_limit_middleware(app):
    app.add_middleware(RateLimitMiddleware)