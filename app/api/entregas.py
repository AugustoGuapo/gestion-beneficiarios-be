"""Endpoints del módulo de Entregas (HU-22)."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.services.entrega_service import EntregaService
from app.core.security import get_current_user
from app.infrastructure.db.session import get_db
from app.schema.entrega_schema import EntregaCreate, EntregaResponse

router = APIRouter(prefix="/entregas", tags=["entregas"])


@router.post(
    "/",
    response_model=EntregaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar entrega individual (HU-22)",
)
async def registrar_entrega(
    payload: EntregaCreate,
    _current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Registra una entrega individual a una familia.

    **Comportamiento (transaccional):**
    1. Valida que exista la familia y los recursos.
    2. Valida stock suficiente por recurso (en la bodega indicada o resolviendo la
       primera bodega con stock disponible).
    3. Genera un código `ENT-AAAA-NNNNN` único y secuencial por año.
    4. Inserta la `entrega` con estado='ENTREGADA', sus líneas en `detalle_entrega`
       y los movimientos `SALIDA` en `movimiento_inventario`.

    **Errores comunes:**
    - 404: familia, recurso o bodega no encontrados.
    - 409: stock insuficiente o conflicto de integridad (código duplicado).
    """
    return await EntregaService.registrar_entrega(db=db, payload=payload)
