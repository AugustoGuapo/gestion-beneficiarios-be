from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_db
from app.core.security import get_current_user
from app.core.constants import UserRole
from app.application.services.user_service import UserService
from app.schema.user_schema import (
    UserCreate, UserResponse, UserUpdate, UserListResponse
)

router = APIRouter(prefix="/users", tags=["usuarios"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Crear usuario")
async def create_user(
    user_create: UserCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crear un nuevo usuario en el sistema.

    **Permisos:** Solo ADMIN y COORDINADOR_LOGISTICA pueden crear usuarios
    """
    # Verificar permisos
    if current_user["rol"] not in [UserRole.ADMIN.value, UserRole.COORDINADOR_LOGISTICA.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para crear usuarios"
        )

    user = await UserService.create_user(db, user_create)
    return user


@router.get("/", response_model=list[UserListResponse], summary="Listar usuarios")
async def list_users(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar todos los usuarios del sistema.

    **Permisos:** Requiere estar autenticado
    """
    # Restringir listado completo a roles administrativos (principio de mínimo privilegio)
    admin_roles = [
        UserRole.ADMIN.value,
        UserRole.COORDINADOR_LOGISTICA.value
    ]

    if current_user["rol"] not in admin_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para listar todos los usuarios"
        )

    users = await UserService.get_all_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse, summary="Obtener usuario por ID")
async def get_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener los detalles de un usuario específico.

    **Lógica de autorización (mínimo privilegio):**
    - ✅ ADMIN: Puede consultar cualquier usuario
    - ✅ COORDINADOR_LOGISTICA: Puede consultar cualquier usuario (es rol administrativo)
    - ❌ Otros roles: Solo pueden consultar su propia información

    **Permisos:**
    - Debe estar autenticado
    - Acceso restringido por rol y propiedad de datos
    """
    # Roles que tienen permiso para consultar cualquier usuario
    admin_roles = [
        UserRole.ADMIN.value,
        UserRole.COORDINADOR_LOGISTICA.value
    ]

    # Verificar autorización: solo ADMIN/COORDINADOR pueden ver otros usuarios
    if current_user["rol"] not in admin_roles and current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para consultar información de otros usuarios"
        )

    user = await UserService.get_user_by_id(db, user_id)
    return user


@router.put("/{user_id}", response_model=UserResponse, summary="Actualizar usuario")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar información de un usuario.

    **Permisos:** Solo ADMIN puede actualizar cualquier usuario. Otros pueden actualizar su propio perfil
    """
    # Verificar permisos
    if current_user["rol"] != UserRole.ADMIN.value and current_user["user_id"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo puedes actualizar tu propio perfil"
        )

    user = await UserService.update_user(db, user_id, user_update)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar usuario")
async def deactivate_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Desactivar un usuario (desactivación lógica, no eliminación física).

    El usuario con activo=false no podrá iniciar sesión.

    **Permisos:** Solo ADMIN puede desactivar usuarios
    """
    if current_user["rol"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden desactivar usuarios"
        )

    await UserService.deactivate_user(db, user_id)
    return None


@router.post("/{user_id}/activate", response_model=UserResponse, summary="Activar usuario")
async def activate_user(
    user_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Activar un usuario desactivado (establecer activo=true).

    El usuario podrá volver a iniciar sesión.

    **Permisos:** Solo ADMIN puede activar usuarios
    """
    if current_user["rol"] != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo administradores pueden activar usuarios"
        )

    user = await UserService.activate_user(db, user_id)
    return user

