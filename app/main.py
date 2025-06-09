from fastapi import FastAPI
from tortoise import Tortoise
from app.database.connection import init_db
from app.middleware.cors import add_cors_middleware
from app.middleware.logger import add_logging_middleware
from app.middleware.error_handler import add_error_handler_middleware
from app.middleware.gzip import add_gzip_middleware
from app.middleware.rate_limit import add_rate_limit_middleware
from app.middleware.timeout import add_timeout_middleware
from app.middleware.auth import add_auth_middleware
from app.logging.config import setup_logging
from app.routes.health_api import router as health_router
from app.routes.roles import router as roles_router
from app.routes.user import router as users_router
from app.routes.tokens import router as token_router
from app.routes.classes import router as classes_router
from app.routes.bookings import router as bookings_router
from app.database.models.roles import Role
from app.database.models.enums import RecordStatus
import logging

setup_logging()
logger = logging.getLogger("devanchor.main")

app = FastAPI()

add_cors_middleware(app)
add_logging_middleware(app)
add_gzip_middleware(app)
add_rate_limit_middleware(app)
add_timeout_middleware(app)
add_auth_middleware(app)
add_error_handler_middleware(app)

api_prefix="/api/v1"
app.include_router(health_router, prefix=api_prefix)
app.include_router(roles_router, prefix=api_prefix)
app.include_router(users_router, prefix=api_prefix)
app.include_router(token_router, prefix=api_prefix)
app.include_router(classes_router, prefix=api_prefix)
app.include_router(bookings_router, prefix=api_prefix)

@app.on_event("startup")
async def startup_event():
    logger.info("Application startup initiated")
    try:
        success, reason = await init_db()
        if success:
            if "No schema changes" in reason:
                logger.info("No Schema Changes Detected, Skipping Migrations")
            else:
                logger.info("Migrations Done")
        else:
            logger.error(f"Migration Not Done Due to {reason}")

        client_role = await Role.get_or_none(name="client")
        if not client_role:
            client_role = await Role.create(
                name="client",
                description="Default role for fitness studio clients",
                status=RecordStatus.active
            )
            logger.info("Seeded 'client' role")
        else:
            logger.debug("'client' role already exists")

        connection = Tortoise.get_connection("default")
        await connection.execute_query("SELECT 1")
        logger.info("Database connection verified")
    except Exception as e:
        logger.error(f"Unexpected error during startup: {str(e)}", exc_info=True)
        raise RuntimeError(f"Startup failure: {str(e)}")
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown initiated")
    await Tortoise.close_connections()