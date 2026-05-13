from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.infrastructure.db.session import get_db
from app.domain.models.user import User
from app.core.security import create_access_token


router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Autenticación mock - cualquier contraseña si el usuario existe."""
    result = await db.execute(select(User).where(User.nombre == request.username))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    access_token = create_access_token(request.username)
    return {"access_token": access_token, "token_type": "bearer"}
