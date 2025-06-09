from tortoise import Tortoise
from tortoise.exceptions import OperationalError
from app.config.settings import settings
from typing import AsyncGenerator, Tuple
from aerich import Command
import logging
import os
import time

logger = logging.getLogger("devanchor.main")

def get_db_config():
    config = {
        "DB_FILE": settings.DB_FILE,
    } if settings.DB_ENV == "production" else {
        "DB_FILE": settings.DB_FILE_TEST,
    }
    return config

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {
                "file_path": get_db_config()["DB_FILE"],
            }
        }
    },
    "apps": {
        "models": {
            "models": ["app.database.models", "aerich.models"],
            "default_connection": "default",
        }
    }
}

async def init_db() -> Tuple[bool, str]:
    """
    Initialize Tortoise ORM and check/apply migrations using Aerich.
    Skips initialization if already done and only generates new migrations for unapplied model changes.
    Returns: (success: bool, reason: str)
    """
    try:
        # Initialize Tortoise ORM
        logger.debug("Initializing Tortoise ORM")
        await Tortoise.init(config=TORTOISE_ORM)

        # Initialize Aerich
        logger.debug("Initializing Aerich command")
        aerich_command = Command(tortoise_config=TORTOISE_ORM, app="models", location="./migrations")
        await aerich_command.init()

        # Check if aerich table exists
        logger.debug("Checking for aerich table")
        connection = Tortoise.get_connection("default")
        try:
            await connection.execute_query("SELECT 1 FROM aerich LIMIT 1")
            aerich_table_exists = True
        except OperationalError:
            aerich_table_exists = False

        # Check for existing migration files
        migrations_dir = "./migrations/models"
        os.makedirs(migrations_dir, exist_ok=True)
        existing_migrations = set(os.listdir(migrations_dir))
        has_migration_files = bool(existing_migrations)

        # Initialize database if aerich table and migrations are missing
        if not aerich_table_exists and not has_migration_files:
            logger.info("Aerich table and migrations not found, initializing database")
            await aerich_command.init_db(safe=False)
            logger.info("Aerich database initialized")
            return True, "Aerich database initialized with initial migrations"
        elif not aerich_table_exists:
            logger.warning("Aerich table missing but migrations exist")
            return False, (
                "Aerich table not found but migration files exist. "
                "Run 'aerich init-db' to create the aerich table, "
                "then 'aerich upgrade' to apply existing migrations."
            )

        # Apply any unapplied migrations
        logger.debug("Applying unapplied migrations")
        await aerich_command.upgrade()

        # Check for model changes by attempting to generate a migration
        logger.debug("Checking for model changes")
        before_migrations = set(os.listdir(migrations_dir))
        migration_name = f"auto_migration_{int(time.time())}"
        await aerich_command.migrate(migration_name)

        # Check if a new migration file was created
        after_migrations = set(os.listdir(migrations_dir))
        new_migrations = after_migrations - before_migrations

        if not new_migrations:
            return True, "No schema changes detected, skipping migrations"

        # Apply new migrations
        logger.debug("Applying new migrations")
        await aerich_command.upgrade()
        return True, f"Schema migrations applied successfully: {new_migrations}"
    except OperationalError as e:
        logger.error(f"Database error during initialization: {str(e)}", exc_info=True)
        return False, (
            f"Migration failed due to database error: {str(e)}. "
            "Check your database configuration (file path). "
            "Ensure the database file is accessible and run 'aerich init-db' manually."
        )
    except FileExistsError as e:
        logger.error(f"Migration initialization error: {str(e)}", exc_info=True)
        return False, (
            f"Migration initialization failed: {str(e)}. "
            "Existing migration files may be causing conflicts. "
            "Remove or rename 'migrations/models/0_*.py' files and run 'aerich init-db', "
            "then 'aerich migrate --name fix_schema' and 'aerich upgrade'."
        )
    except Exception as e:
        logger.error(f"Unexpected error during migration: {str(e)}", exc_info=True)
        return False, (
            f"Unexpected error during migration: {str(e)}. "
            "Verify aerich.ini and TORTOISE_ORM settings. "
            "Run 'aerich init -t app.database.connection.TORTOISE_ORM' and 'aerich init-db', "
            "then 'aerich migrate --name fix_schema' and 'aerich upgrade'."
        )

async def get_db() -> AsyncGenerator:
    async with Tortoise.get_connection("default"):
        yield