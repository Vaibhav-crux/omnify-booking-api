from starlette.middleware.gzip import GZipMiddleware
import logging

class CustomGZipMiddleware(GZipMiddleware):
    def __init__(self, app, minimum_size=1000):
        super().__init__(app, minimum_size=minimum_size)
        self.logger = logging.getLogger("devanchor.middleware.gzip")

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if response.headers.get("Content-Encoding") == "gzip":
            self.logger.debug(f"Compressed response for {request.url}")
        return response

def add_gzip_middleware(app):
    app.add_middleware(CustomGZipMiddleware)