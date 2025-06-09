import jwt
from datetime import datetime, timedelta, timezone
from app.config.settings import settings
from app.utils.constants import ErrorMessages
import logging

logger = logging.getLogger("devanchor.utils.jwt")

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        logger.debug("Access token created")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create access token: {str(e)}", exc_info=True)
        raise

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    try:
        encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
        logger.debug("Refresh token created")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create refresh token: {str(e)}", exc_info=True)
        raise

def decode_token(token: str) -> dict:
    if not token or len(token.split(".")) != 3:
        logger.error("Invalid JWT token format: incorrect number of segments")
        raise jwt.InvalidTokenError(ErrorMessages.UNAUTHORIZED)

    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        raise jwt.InvalidTokenError(ErrorMessages.UNAUTHORIZED)
    except jwt.InvalidTokenError as e:
        logger.error(f"Invalid token: {str(e)}")
        raise jwt.InvalidTokenError(ErrorMessages.UNAUTHORIZED)