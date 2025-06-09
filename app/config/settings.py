from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    # Production DB Config
    DB_FILE = os.getenv("DB_FILE")

    # Active DB Environment
    DB_ENV = os.getenv("DB_ENV", "production")

    # Application Environment
    environment = os.getenv("ENVIRONMENT", "production")  # development, production, or testing

    # Test DB Config (for test environment)
    DB_FILE_TEST = os.getenv("DB_FILE_TEST", "./test.db")

    # JWT Config
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "60"))

settings = Settings()