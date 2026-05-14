from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.db.session import get_db
from app.domain.models.bodega import Bodega
from app.domain.models.zona import Zona
from app.core.security import get_current_user
from app.schema.bodega_schema import BodegaCreate, BodegaResponse

router = APIRouter(prefix="/bodegas", tags=["bodegas"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def _bodega_to_payload(bodega: Bodega) -> dict:
    """Convert ORM model to response payload"""
    latitud = getattr(bodega, "latitud")
    longitud = getattr(bodega, "longitud")
    capacidad_max_kg = getattr(bodega, "capacidad_max_kg")
    peso_actual_kg = getattr(bodega, "peso_actual_kg")
    zona_id = getattr(bodega, "zona_id")
    capacidad = float(capacidad_max_kg) if capacidad_max_kg is not None else 0.0
    peso = float(peso_actual_kg) if peso_actual_kg is not None else 0.0
    porcentaje = (peso / capacidad * 100) if capacidad > 0 else 0.0
    return {
        "id_bodega": bodega.id_bodega,
        "nombre": bodega.nombre,
        "latitud": float(latitud) if latitud is not None else 0.0,
        "longitud": float(longitud) if longitud is not None else 0.0,
        "capacidad_max_kg": capacidad,
        "peso_actual_kg": peso,
        "zona_id": int(zona_id) if zona_id is not None else 0,
        "peso_porcentaje": porcentaje,
        "has_alerta": porcentaje >= 85,
    }


@router.get("/", response_model=list[BodegaResponse])
async def get_bodegas(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Listar todas las bodegas (HU-11)"""
    get_current_user(token)
    result = await db.execute(select(Bodega))
    bodegas = result.scalars().all()
    return [_bodega_to_payload(bodega) for bodega in bodegas]


@router.get("/{bodega_id}", response_model=BodegaResponse)
async def get_bodega(
    bodega_id: int,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Obtener detalle de una bodega específica (HU-11)"""
    get_current_user(token)
    result = await db.execute(select(Bodega).where(Bodega.id_bodega == bodega_id))
    bodega = result.scalar_one_or_none()
    if bodega is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bodega no encontrada",
        )
    return _bodega_to_payload(bodega)


@router.post("/", response_model=BodegaResponse, status_code=status.HTTP_201_CREATED)
async def create_bodega(
    bodega: BodegaCreate,
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Crear nueva bodega - HU-11

    Regla RN-03: Si peso_actual_kg > capacidad_maxima_kg, retorna 400 BadRequest
    Alerta: Si peso_actual_kg >= 85% de capacidad, retorna has_alerta=true
    """
    get_current_user(token)

    zona_result = await db.execute(select(Zona).where(Zona.id_zona == bodega.zona_id))
    zona = zona_result.scalar_one_or_none()
    if zona is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zona no encontrada",
        )

    # Validar RN-03: El peso no debe exceder la capacidad
    if bodega.peso_actual_kg > bodega.capacidad_max_kg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Peso actual ({bodega.peso_actual_kg} kg) no puede exceder "
                f"capacidad máxima ({bodega.capacidad_max_kg} kg)"
            ),
        )

    new_bodega = Bodega(
        nombre=bodega.nombre,
        latitud=bodega.latitud,
        longitud=bodega.longitud,
        capacidad_max_kg=bodega.capacidad_max_kg,
        peso_actual_kg=bodega.peso_actual_kg,
        zona_id=bodega.zona_id,
    )
    db.add(new_bodega)
    await db.commit()
    await db.refresh(new_bodega)

    return _bodega_to_payload(new_bodega)
