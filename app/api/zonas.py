from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.infrastructure.db.session import get_db
from app.domain.models.zona import Zona
from app.core.security import get_current_user, check_role
from app.core.constants import UserRole
from app.schema.zona_schema import ZonaResponse

router = APIRouter(prefix="/zonas", tags=["zonas"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


@router.get("/", response_model=list[ZonaResponse])
async def get_zonas(
    current_user: dict = Depends(check_role([
        UserRole.ADMIN,
        UserRole.CENSADOR,
        UserRole.COORDINADOR_LOGISTICA,
        UserRole.FUNCIONARIO_CONTROL,
    ])),
    db: Session = Depends(get_db),
):
    result = await db.execute(select(Zona))
    zonas = result.scalars().all()
    return zonas


@router.get("/{zona_id}", response_model=ZonaResponse)
async def get_zona(
    zona_id: int,
    current_user: dict = Depends(check_role([
        UserRole.ADMIN,
        UserRole.CENSADOR,
        UserRole.COORDINADOR_LOGISTICA,
        UserRole.FUNCIONARIO_CONTROL,
    ])),
    db: Session = Depends(get_db),
):
    result = await db.execute(select(Zona).where(Zona.id_zona == zona_id))
    zona = result.scalar_one_or_none()
    return zona
