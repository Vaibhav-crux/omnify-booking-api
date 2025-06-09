from app.config.settings import settings

def get_production_db_config():
    return {
        "DB_FILE": settings.DB_FILE,
    }