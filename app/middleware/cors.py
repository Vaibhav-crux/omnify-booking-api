from fastapi.middleware.cors import CORSMiddleware

def add_cors_middleware(app):
    # Configure CORS middleware
    app.add_middleware(
        CORSMiddleware,          # FastAPI CORS middleware
        allow_origins=["*"],     # Permit requests from all origins
        allow_credentials=True,  # Enable credentials support
        allow_methods=["*"],     # Allow all HTTP methods
        allow_headers=["*"],     # Permit all headers
    )