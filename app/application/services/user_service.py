from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.domain.models.user import User
from app.core.security import hash_password, verify_password
from app.schema.user_schema import UserCreate, UserUpdate


class UserService:
    """Servicio de lógica de negocio para usuarios"""

    @staticmethod
    async def create_user(db: AsyncSession, user_create: UserCreate) -> User:
        """Crea un nuevo usuario."""
        try:
            # Verificar si el email ya existe
            result = await db.execute(
                select(User).where(User.correo == user_create.correo)
            )
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El correo ya está registrado"
                )

            # Crear usuario con contraseña hasheada
            new_user = User(
                nombre_completo=user_create.nombre_completo,
                correo=user_create.correo,
                password_hash=hash_password(user_create.password),
                rol=user_create.rol.value,
                activo=True
            )

            db.add(new_user)
            await db.commit()
            await db.refresh(new_user)
            return new_user

        except IntegrityError as e:
            await db.rollback()
            # Intentar identificar si la violación corresponde a una restricción UNIQUE
            # sobre el campo `correo`. Dependiendo del driver (psycopg2/asyncpg)
            # la información puede estar en diferentes atributos.
            msg = "Violación de integridad en la base de datos"
            try:
                orig = getattr(e, 'orig', None)
                orig_msg = str(orig) if orig is not None else str(e)
            except Exception:
                orig_msg = str(e)

            lower_msg = orig_msg.lower()
            if 'unique' in lower_msg or 'duplicate' in lower_msg or 'violat' in lower_msg:
                # Si el mensaje menciona el correo explícitamente, devolver mensaje específico
                if 'correo' in lower_msg or 'usuario_correo' in lower_msg or 'email' in lower_msg:
                    msg = 'El correo ya está registrado'
                else:
                    # Mensaje seguro y no revelador cuando no podemos identificar el constraint
                    msg = 'Datos duplicados o inválidos'

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=msg
            )

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
        """Obtiene un usuario por ID."""
        result = await db.execute(
            select(User).where(User.id_usuario == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
        return user

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User:
        """Obtiene un usuario por email."""
        result = await db.execute(
            select(User).where(User.correo == email)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
        """Obtiene todos los usuarios con paginación."""
        result = await db.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, user_update: UserUpdate) -> User:
        """Actualiza un usuario (actualización lógica)."""
        user = await UserService.get_user_by_id(db, user_id)

        # Actualizar solo los campos proporcionados
        if user_update.nombre_completo:
            user.nombre_completo = user_update.nombre_completo
        if user_update.rol:
            user.rol = user_update.rol.value
        if user_update.activo is not None:
            user.activo = user_update.activo

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def deactivate_user(db: AsyncSession, user_id: int) -> User:
        """Desactiva un usuario (desactivación lógica)."""
        user = await UserService.get_user_by_id(db, user_id)
        user.activo = False

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def activate_user(db: AsyncSession, user_id: int) -> User:
        """Activa un usuario desactivado."""
        user = await UserService.get_user_by_id(db, user_id)
        user.activo = True

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
        """Autentica un usuario con email y contraseña."""
        user = await UserService.get_user_by_email(db, email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )

        # Verificar contraseña
        if not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales inválidas"
            )

        # Verificar que el usuario esté activo
        if not user.activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario inactivo. Contacte al administrador"
            )

        return user

    
