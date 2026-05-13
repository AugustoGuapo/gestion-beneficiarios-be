from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_db
from app.domain.models.user import User
from app.core.security import get_current_user
from app.schema.user_schema import UserResponse, UserCreate

router = APIRouter(prefix="/users", tags=["users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.get("/", response_model=list[UserResponse])
async def get_users(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    get_current_user(token)
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    get_current_user(token)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user


@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    get_current_user(token)
    new_user = User(nombre=user.nombre, rol=user.rol)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
