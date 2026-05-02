from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, status
from app.core.config import settings


def create_access_token(username: str) -> str:
    """Genera un JWT con el username."""
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    to_encode = {"sub": username, "exp": expire}
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verifica el token JWT y retorna los datos."""
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token: str) -> str:
    """Dependency para obtener el usuario actual del token."""
    payload = verify_token(token)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    return username