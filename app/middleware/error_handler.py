from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import traceback

class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("devanchor.middleware.error")

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            log_data = {
                "status_code": e.status_code,
                "detail": e.detail,
                "path": str(request.url.path),
                "method": request.method
            }
            self.logger.error("HTTP Exception", extra=log_data)
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            stack_trace = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            log_data = {
                "error_type": str(type(e).__name__),
                "error_message": str(e),
                "stack_trace": stack_trace,
                "path": str(request.url.path),
                "method": request.method
            }
            self.logger.error("Unhandled exception", extra=log_data)
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"}
            )

def add_error_handler_middleware(app):
    app.add_middleware(ErrorHandlerMiddleware)