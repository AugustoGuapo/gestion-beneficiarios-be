from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_db
from app.domain.models.zona import Zona
from app.core.security import get_current_user
from app.schema.zona_schema import ZonaCreate, ZonaResponse

router = APIRouter(prefix="/zonas", tags=["zonas"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.get("/", response_model=list[ZonaResponse])
async def get_zonas(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    get_current_user(token)
    result = await db.execute(select(Zona))
    zonas = result.scalars().all()
    return zonas


@router.get("/{zona_id}", response_model=ZonaResponse)
async def get_zona(
    zona_id: int, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    get_current_user(token)
    result = await db.execute(select(Zona).where(Zona.id_zona == zona_id))
    zona = result.scalar_one_or_none()
    if zona is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona no encontrada",
        )
    return zona


@router.post("/", response_model=ZonaResponse, status_code=status.HTTP_201_CREATED)
async def create_zona(
    zona: ZonaCreate, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    get_current_user(token)
    new_zona = Zona(nombre=zona.nombre, nivel_riesgo=zona.nivel_riesgo.value)
    db.add(new_zona)
    await db.commit()
    await db.refresh(new_zona)
    return new_zona
