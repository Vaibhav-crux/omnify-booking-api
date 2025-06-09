from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time

class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("devanchor.middleware.http")

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        request_details = {
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "query_params": dict(request.query_params),
        }
        
        self.logger.info(
            "Incoming request",
            extra={"request": request_details}
        )
        
        try:
            response = await call_next(request)
            
            duration = time.time() - start_time
            
            self.logger.info(
                "Completed request",
                extra={
                    "request": request_details,
                    "response": {
                        "status_code": response.status_code,
                        "duration_ms": round(duration * 1000, 2)
                    }
                }
            )
            
            return response
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                "Request failed",
                extra={
                    "request": request_details,
                    "error": str(e),
                    "duration_ms": round(duration * 1000, 2)
                },
                exc_info=True
            )
            raise

def add_logging_middleware(app):
    app.add_middleware(LoggingMiddleware)