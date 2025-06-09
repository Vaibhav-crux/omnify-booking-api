from app.config.settings import settings

def get_test_db_config():
    return {
        "DB_HOST": settings.DB_HOST_TEST,
        "DB_PORT": settings.DB_PORT_TEST,
        "DB_USERNAME": settings.DB_USERNAME_TEST,
        "DB_PASSWORD": settings.DB_PASSWORD_TEST,
        "DB_DATABASE": settings.DB_DATABASE_TEST
    }