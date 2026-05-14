from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_db
from app.domain.models.refugio import Refugio
from app.domain.models.zona import Zona
from app.core.security import get_current_user
from app.schema.refugio_schema import RefugioCreate, RefugioResponse

router = APIRouter(prefix="/refugios", tags=["refugios"])


def _refugio_to_payload(refugio: Refugio) -> dict:
    """Convert ORM model to response payload"""
    latitud = getattr(refugio, "latitud")
    longitud = getattr(refugio, "longitud")
    capacidad_maxima = getattr(refugio, "capacidad_maxima_personas")
    ocupacion_actual = getattr(refugio, "ocupacion_actual")
    capacidad = float(capacidad_maxima) if capacidad_maxima is not None else 0.0
    ocupacion = float(ocupacion_actual) if ocupacion_actual is not None else 0.0
    ocupacion_porcentaje = (ocupacion / capacidad * 100) if capacidad > 0 else 0.0
    return {
        "id": refugio.id,
        "nombre": refugio.nombre,
        "ubicacion_textual": refugio.ubicacion_textual,
        "latitud": float(latitud) if latitud is not None else 0.0,
        "longitud": float(longitud) if longitud is not None else 0.0,
        "capacidad_maxima_personas": int(capacidad) if capacidad_maxima is not None else 0,
        "ocupacion_actual": int(ocupacion) if ocupacion_actual is not None else 0,
        "zona_id": refugio.zona_id,
        "fecha_registro": refugio.fecha_registro,
        "ocupacion_porcentaje": ocupacion_porcentaje,
        "has_alerta": ocupacion_porcentaje > 90,
    }


@router.get("/", response_model=list[RefugioResponse])
async def get_refugios(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Refugio))
    refugios = result.scalars().all()
    return [_refugio_to_payload(refugio) for refugio in refugios]


@router.get("/{refugio_id}", response_model=RefugioResponse)
async def get_refugio(
    refugio_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Refugio).where(Refugio.id == refugio_id))
    refugio = result.scalar_one_or_none()
    if refugio is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refugio no encontrado",
        )
    return _refugio_to_payload(refugio)


@router.post("/", response_model=RefugioResponse, status_code=status.HTTP_201_CREATED)
async def create_refugio(
    refugio: RefugioCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if refugio.zona_id is not None:
        zona_result = await db.execute(select(Zona).where(Zona.id_zona == refugio.zona_id))
        zona = zona_result.scalar_one_or_none()
        if zona is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Zona no encontrada",
            )

    new_refugio = Refugio(
        nombre=refugio.nombre,
        ubicacion_textual=refugio.ubicacion_textual,
        latitud=refugio.latitud,
        longitud=refugio.longitud,
        capacidad_maxima_personas=refugio.capacidad_maxima_personas,
        ocupacion_actual=refugio.ocupacion_actual,
        zona_id=refugio.zona_id,
    )

    db.add(new_refugio)
    await db.commit()
    await db.refresh(new_refugio)

    return _refugio_to_payload(new_refugio)
