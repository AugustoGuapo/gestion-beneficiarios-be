from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.security import check_role, get_current_user
from app.domain.models.zona import Zona
from app.infrastructure.db.session import get_db
from app.schema.zona_schema import ZonaCreate, ZonaResponse

router = APIRouter(prefix="/zonas", tags=["zonas"])


def _zona_to_payload(zona: Zona) -> dict:
    return {
        "id_zona": zona.id_zona,
        "nombre": zona.nombre,
        "nivel_riesgo": zona.nivel_riesgo_tipo or "bajo",
    }


@router.get("/", response_model=list[ZonaResponse])
async def get_zonas(
    current_user: dict = Depends(
        check_role(
            [
                UserRole.ADMIN,
                UserRole.CENSADOR,
                UserRole.COORDINADOR_LOGISTICA,
                UserRole.FUNCIONARIO_CONTROL,
            ]
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Zona))
    zonas = result.scalars().all()
    return [_zona_to_payload(zona) for zona in zonas]


@router.get("/{zona_id}", response_model=ZonaResponse)
async def get_zona(
    zona_id: int,
    current_user: dict = Depends(
        check_role(
            [
                UserRole.ADMIN,
                UserRole.CENSADOR,
                UserRole.COORDINADOR_LOGISTICA,
                UserRole.FUNCIONARIO_CONTROL,
            ]
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Zona).where(Zona.id_zona == zona_id))
    zona = result.scalar_one_or_none()
    if zona is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona no encontrada",
        )
    return _zona_to_payload(zona)


@router.post("/", response_model=ZonaResponse, status_code=status.HTTP_201_CREATED)
async def create_zona(
    zona: ZonaCreate,
    current_user: dict = Depends(
        check_role(
            [
                UserRole.ADMIN,
                UserRole.CENSADOR,
            ]
        )
    ),
    db: AsyncSession = Depends(get_db),
):
    new_zona = Zona(nombre=zona.nombre, nivel_riesgo_tipo=zona.nivel_riesgo)
    db.add(new_zona)
    await db.commit()
    await db.refresh(new_zona)
    return _zona_to_payload(new_zona)
