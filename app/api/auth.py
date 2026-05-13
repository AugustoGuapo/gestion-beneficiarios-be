from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_db
from app.application.services.user_service import UserService
from app.core.security import create_access_token, get_current_user
from app.schema.user_schema import UserLoginRequest, UserLoginResponse


router = APIRouter(prefix="/auth", tags=["autenticación"])


@router.post("/login", response_model=UserLoginResponse, summary="Login de usuario")
async def login(
    login_request: UserLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Autenticarse en el sistema con email y contraseña.

    Retorna un token JWT válido por la duración configurada en el servidor.

    **Requisitos:**
    - El usuario debe existir
    - Las credenciales deben ser correctas
    - El usuario debe estar activo (no desactivado)
    """
    # Autenticar usuario
    user = await UserService.authenticate_user(
        db,
        login_request.correo,
        login_request.password
    )

    # Crear token JWT
    access_token = create_access_token(user.id_usuario, user.correo, user.rol)

    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        usuario={
            "id_usuario": user.id_usuario,
            "nombre_completo": user.nombre_completo,
            "correo": user.correo,
            "rol": user.rol,
            "activo": user.activo
        }
    )


@router.post("/refresh-token", response_model=UserLoginResponse, summary="Refrescar token")
async def refresh_token(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Refrescar el token JWT para extender la sesión.

    Retorna un nuevo token y los datos del usuario autenticado.

    Nota: Este endpoint requiere un token válido en el header.
    """
    # Obtener datos completos del usuario desde DB
    user = await UserService.get_user_by_id(db, current_user["user_id"])

    # Crear nuevo token JWT
    access_token = create_access_token(
        user.id_usuario,
        user.correo,
        user.rol
    )

    # Devolver respuesta estandarizada igual a /login
    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        usuario={
            "id_usuario": user.id_usuario,
            "nombre_completo": user.nombre_completo,
            "correo": user.correo,
            "rol": user.rol,
            "activo": user.activo
        }
    )
