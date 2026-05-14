from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.constants import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Hashea una contraseña con bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, email: str, rol: str) -> str:
    """Genera un JWT con datos del usuario."""
    expire = datetime.utcnow() + timedelta(minutes=settings.jwt_expiration_minutes)
    to_encode = {
        "sub": email,
        "user_id": user_id,
        "rol": rol,
        "exp": expire,
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verifica el token JWT y retorna los datos."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """Dependency para obtener el usuario actual del token."""
    payload = verify_token(token)
    email = payload.get("sub")
    user_id = payload.get("user_id")
    rol = payload.get("rol")

    if email is None or user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
        )

    return {"email": email, "user_id": user_id, "rol": rol}


def check_role(required_roles: list[UserRole]) -> Callable:
    """Factory para crear un guard que valida roles específicos."""
    async def role_checker(
        current_user: Annotated[dict, Depends(get_current_user)],
    ) -> dict:
        user_rol = current_user.get("rol")
        if user_rol not in [role.value for role in required_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Acceso denegado. Roles requeridos: {[role.value for role in required_roles]}"
                ),
            )
        return current_user

    return role_checker


def get_username_from_authorization_header(auth_header: str | None) -> str | None:
    """Extrae el usuario desde el header Authorization si el token es válido."""
    if not auth_header:
        return None

    if not auth_header.lower().startswith("bearer "):
        return None

    token = auth_header.split(" ")[1]

    try:
        payload = verify_token(token)
        return payload.get("sub")
    except HTTPException:
        return None
