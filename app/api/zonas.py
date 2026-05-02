from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.infrastructure.db.session import get_db
from app.domain.models.zona import Zona
from app.core.security import get_current_user
from app.schema.zona_schema import ZonaResponse

router = APIRouter(prefix="/zonas", tags=["zonas"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.get("/", response_model=list[ZonaResponse])
async def get_zonas(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    get_current_user(token)
    result = await db.execute(select(Zona))
    zonas = result.scalars().all()
    return zonas


@router.get("/{zona_id}", response_model=ZonaResponse)
async def get_zona(
    zona_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    get_current_user(token)
    result = await db.execute(select(Zona).where(Zona.id_zona == zona_id))
    zona = result.scalar_one_or_none()
    return zona
